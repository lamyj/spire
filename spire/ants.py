import os

from .task_factory import TaskFactory

class Registration(TaskFactory):
    """ Register two images using ANTs. fixed and moving describe the respective
        images, and may include an optional volume to use in case of 4D images:
        passing (foo.nii.gz,0) will use the first 3D volume of the 4D foo.nii.gz
        for the registration. transform must be one of "rigid", "affine" or 
        "syn". initial_transforms must be either None (its default value) or a
        list of transforms.
        
        This task stores the transforms in a specific member, in the order they
        should be passed to ApplyTransforms.
    """
    def __init__(
            self, fixed, moving, transform, prefix, 
            save_warped=True, quick=False, precision="double", 
            initial_transforms=None):
        TaskFactory.__init__(self, str(prefix))
        self.quick = quick
        
        # Prepare the volume extraction if necessary
        self.file_dep = []
        volumes = []
        extractions = []
        removals = []
        for name, data in [["fixed", fixed], ["moving", moving]]:
            path, index = _get_path_and_index(data)
            self.file_dep.append(path)
            
            if None not in (path, index):
                # NOTE Named is based on target, it should be unique since 
                # target paths are.
                temp = os.path.join(
                    os.path.dirname(prefix), 
                    "__{}_{}_{}.nii.gz".format(
                        os.path.basename(prefix), name, index))
                
                volumes.append(temp)
                extractions.append(
                    ["ImageMath", "4", temp, "ExtractSlice", path, str(index)])
                removals.append(["rm", temp])
            else:
                volumes.append(path)
        
        fixed_volume, moving_volume = volumes
        
        # Prepare the registration command
        registration = [
            "antsRegistration",
            "--dimensionality", "3", 
            "--float", "0" if precision == "double" else "1",
            "--interpolation", "Linear", 
            "--winsorize-image-intensities", "[0.005,0.995]",
            "--use-histogram-matching", "0",
        ]
        
        # Update the outputs of the command
        output_images = []
        if save_warped:
            registration += [
                "--output", 
                "[{},{}Warped.nii.gz,{}InverseWarped.nii.gz]".format(
                    prefix, prefix, prefix)]
            output_images += [
                "{}Warped.nii.gz".format(prefix), 
                "{}InverseWarped.nii.gz".format(prefix)]
        else:
            registration += ["--output", prefix]
        
        # Update the command with the transforms. WARNING: antsApplyTransforms
        # uses a transform _stack_.
        self.transforms = []
        registration += self.initial_stage(
            fixed_volume, moving_volume, initial_transforms)
        if transform.lower() in ["rigid", "affine", "syn"]:
            registration += self.rigid_stage(fixed_volume, moving_volume)
            self.transforms.insert(0, "{}{}".format(prefix, "0GenericAffine.mat"))
        if transform.lower() in ["affine", "syn"]:
            registration += self.affine_stage(fixed_volume, moving_volume)
        if transform.lower() == "syn":
            registration += self.syn_stage(fixed_volume, moving_volume)
            self.transforms.insert(0, "{}{}".format(prefix, "1Warp.nii.gz"))
        
        # self.file_dep is already OK
        self.targets = (
            self.transforms 
            + (
                ["{}{}".format(prefix, "1InverseWarp.nii.gz")] 
                if transform.lower() == "syn" else [])
            + output_images)
        self.actions = extractions + [registration] + removals
        
    @property
    def inverse_transforms(self):
        """ The list of transforms from fixed to moving, in the order they 
            should be passed to ApplyTransforms.
        """
        
        result = []
        for transform in self.transforms[::-1]:
            if transform.endswith("0GenericAffine.mat"):
                result.append([transform, 1])
            else:
                result.append(transform.replace("Warp.nii", "InverseWarp.nii"))
        return result
    
    def initial_stage(self, fixed, moving, initial_transforms):
        if not initial_transforms:
            initial_transforms = ["[{},{},1]".format(fixed, moving)]
        transforms = []
        for item in initial_transforms:
            transforms.extend(["--initial-moving-transform", item])
        return transforms
    
    def rigid_stage(self, fixed, moving):
        return [
            "--transform", "Rigid[0.1]",
            "--metric", "MI[{},{},1,32,Regular,0.25]".format(fixed, moving),
            "--convergence", "[1000x500x250x{},1e-6,10]".format(
                0 if self.quick else 100),
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]
    
    def affine_stage(self, fixed, moving):
        return [
            "--transform", "Affine[0.1]",
            "--metric", "MI[{},{},1,32,Regular,0.25]".format(fixed, moving),
            "--convergence", "[1000x500x250x{},1e-6,10]".format(
                0 if self.quick else 100),
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]
    
    def syn_stage(self, fixed, moving):
        return [
            "--transform", "SyN[0.1,3,0]",
            "--metric", "CC[{},{},1,4]".format(fixed, moving),
            "--convergence", "[100x70x50x{},1e-6,10]".format(
                0 if self.quick else 20),
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]

class ApplyTransforms(TaskFactory):
    """ Apply transforms and resample an image. The reference image may include
        an optional volume to use in case of 4D images: passing (foo.nii.gz,0) 
        will use the first 3D volume of the 4D foo.nii.gz.
    """
    def __init__(
            self, input, reference, transforms, output, 
            interpolation="BSpline", input_image_type="scalar"):
        TaskFactory.__init__(self, str(output))
        
        extraction = []
        removal = []
        
        reference_path, index = _get_path_and_index(reference)
        
        if None not in (reference_path, index):
            # NOTE Named is based on target, it should be unique since 
            # target paths are.
            reference_volume = os.path.join(
                os.path.dirname(output), 
                "__{}_{}.nii.gz".format(os.path.basename(output), index))
        
            extraction = [
                "ImageMath", "4", reference_volume,
                "ExtractSlice", reference_path, str(index)]
            removal = ["rm", reference_volume]
        else:
            reference_volume = reference_path
        
        self.file_dep = [input, reference_path]
        for transform in transforms:
            if isinstance(transform, list):
                self.file_dep.append(transform[0])
            else:
                self.file_dep.append(transform)
        
        self.targets = [output]
        apply_transforms = [
            "antsApplyTransforms",
            "-i", input, "-r", reference_volume, "-o", output, 
            "-n", interpolation, "-e", input_image_type]
        for transform in transforms:
            apply_transforms.append("-t")
            if isinstance(transform, (list, tuple)):
                apply_transforms.append("[{}]".format("{},{}".format(*transform)))
            else:
                apply_transforms.append(transform)
        self.actions = extraction+[apply_transforms]+removal

def _get_path_and_index(data):
    if isinstance(data, (list, tuple)):
        path, index = data
    else:
        path, index = data, None
    return path, index
