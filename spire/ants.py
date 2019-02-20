import os
import tempfile

from .task_factory import TaskFactory

class Registration(TaskFactory):
    """ Register two images using ANTs. fixed and moving describe the respective
        images, and may include an optional volume to use in case of 4D images:
        passing (foo.nii.gz,0) will use the first 3D volume of the 4D foo.nii.gz
        for the registration. transform must be one of "rigid", "affine" or 
        "syn".
    """
    def __init__(self, fixed, moving, transform, prefix, save_warped=True):
        TaskFactory.__init__(self, prefix)
        
        # Prepare the volume extraction if necessary
        self.file_dep = []
        volumes = []
        extractions = []
        removals = []
        for data in fixed, moving:
            if isinstance(data, (list, tuple)):
                path, index = data
                
                self.file_dep.append(path)
                
                fd, temp = tempfile.mkstemp(suffix=".nii.gz")
                os.close(fd)
                
                volumes.append(temp)
                extractions.append(
                    ["ImageMath", "4", temp, "ExtractSlice", path, str(index)])
                removals.append(["rm", temp])
            else:
                self.file_dep.append(data)
                volumes.append(data)
        fixed_volume, moving_volume = volumes
        
        # Prepare the registration command
        registration = [
            "antsRegistration",
            "--dimensionality", "3", "--float", "0",
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
        
        # Update the command with the transforms
        self.transforms = []
        if transform.lower() in ["rigid", "affine", "syn"]:
            registration += self.rigid_stage(fixed_volume, moving_volume)
            self.transforms.append("{}{}".format(prefix, "0GenericAffine.mat"))
        if transform.lower() in ["affine", "syn"]:
            registration += self.affine_stage(fixed_volume, moving_volume)
        if transform.lower() == "syn":
            registration += self.syn_stage(fixed_volume, moving_volume)
            self.transforms.extend([
                "{}{}".format(prefix, suffix) 
                for suffix in ["1Warp.nii.gz", "1InverseWarp.nii.gz"]])
        
        # self.file_dep is already OK
        self.targets = self.transforms + output_images
        self.actions = extractions + [registration] + removals
        
    @property
    def inverse_transforms(self):
        result = []
        for transform in self.transforms[::-1]:
            if transform.endswith("0GenericAffine.mat"):
                result.append([transform, 1])
            else:
                result.append(transform.replace("Warp.nii", "InverseWarp.nii"))
        return result
    
    def rigid_stage(self, fixed, moving):
        return [
            "--initial-moving-transform", "[{},{},1]".format(fixed, moving),
            "--transform", "Rigid[0.1]",
            "--metric", "MI[{},{},1,32,Regular,0.25]".format(fixed, moving),
            "--convergence", "[1000x500x250x100,1e-6,10]",
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]
    
    def affine_stage(self, fixed, moving):
        return [
            "--transform", "Affine[0.1]",
            "--metric", "MI[{},{},1,32,Regular,0.25]".format(fixed, moving),
            "--convergence", "[1000x500x250x100,1e-6,10]",
            "--shrink-factors", "8x4x2x1",
            "--smoothing-sigmas", "3x2x1x0vox",
        ]
    
    def syn_stage(self, fixed, moving):
        return [
            "--transform", "SyN[0.1,3,0]",
            "--metric", "CC[{},{},1,4]".format(fixed, moving),
            "--convergence", "[100x70x50x20,1e-6,10]",
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
        TaskFactory.__init__(self, output)
        
        extraction = []
        removal = []
        if isinstance(reference, (list, tuple)):
            reference_path, index = reference
            fd, reference_volume = tempfile.mkstemp(suffix=".nii.gz")
            os.close(fd)
            
            extraction.append([
                "ImageMath", "4", reference_volume, 
                "ExtractSlice", reference_path, str(index)])
            removal.append(["rm", reference_volume])
        else:
            reference_path = reference
            reference_volume = reference
        
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
