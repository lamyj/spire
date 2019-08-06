import itertools
import pathlib
import textwrap

from .spm_object import SPMObject

class Masking(SPMObject):
    def __init__(self, 
            threshold_mode=None, threshold=None, implicit=True, explicit=""):
        
        super().__init__("spm.stats.factorial_design.masking")
        if threshold_mode not in [None, "absolute", "relative"]:
            raise Exception("Invalid threshold mode: {}".format(threshold_mode))
        self.threshold_mode = threshold_mode
        
        if threshold_mode == "absolute" and threshold is None:
            self.threshold = 100
        elif threshold_mode == "relative" and threshold is None:
            self.threshold = 0.8
        else:
            self.threshold = threshold
        
        self.implicit = implicit
        self.explicit = explicit
        
        self.template = textwrap.dedent("""\
            {%- if threshold_mode == none -%}
            {{ id(index, name) }}.tm.tm_none = 1;
            {%- elif threshold_mode == "absolute" -%}
            {{ id(index, name) }}.tma.athresh = {{ threshold }};
            {%- elif threshold_mode == "relative" -%}
            {{ id(index, name) }}.tmr.rthresh = {{ threshold }};
            {%- endif %}
            {{ id(index, name) }}.im = {{ implicit|int }};
            {{ id(index, name) }}.em = {'{{ explicit}}'};""")

class GlobalCalculation(SPMObject):
    def __init__(self, mode="omit", values=None):
        super().__init__("spm.stats.factorial_design.globalc")
        
        if mode not in ["omit", "user", "mean"]:
            raise Exception("Invalid mode: {}".format(mode))
        self.mode = mode
        
        self.values = values
        
        self.template = textwrap.dedent("""\
            {%- if mode == "omit" -%}
            {{ id(index, name) }}.g_omit = 1;
            {%- elif mode == "user" -%}
            {{ id(index, name) }}.g_user.global_uval = [{{ values|join(";") }}];
            {%- elif mode == "mean" -%}
            {{ id(index, name) }}.g_mean = 1;
            {%- endif -%}""")

class GlobalNormalization(SPMObject):
    def __init__(self, value=None, mode=None):
        super().__init__("spm.stats.factorial_design.globalm")
        
        self.value = value
        
        if mode not in [None, "proportional", "ancova"]:
            raise Exception("Invalid mode: {}".format(mode))
        self.mode = {None: 1, "proportional": 2, "ancova": 3}[mode]
        
        self.template = textwrap.dedent("""\
            {%- if value == none -%}
            {{ id(index, name) }}.gmsca.gmsca_no = 1;
            {%- else -%}
            {{ id(index, name) }}.gmsca.gmsca_yes.gmscv = {{ value }};
            {%- endif %}
            {{ id(index, name) }}.glonorm = {{ mode }};""")

class Covariate(object):
    def __init__(self, cname, values, interactions=None, centering="Overall mean"):
        self.cname = cname
        self.values = values
        
        known_interactions = [None, "With Factor 1", "With Factor 2", "With Factor 3"]
        if interactions not in known_interactions:
            raise Exception("Invalid interactions: {}".format(interactions))
        self.interactions = 1+known_interactions.index(interactions)
        
        known_centering = [
                "Overall mean", 
                "Factor 1 mean", "Factor 2 mean", "Factor 3 mean",
                "No centering", "User specified value", "As implied by ANCOVA", 
                "GM"]
        
        if centering not in known_centering:
            raise Exception("Invalid centering: {}".format(centering))
        self.centering = 1+known_centering.index(centering)

class Covariates(SPMObject):
    def __init__(self, covariates):
        super().__init__("spm.stats.factorial_design.cov")
        self.covariates = covariates
        self.template = textwrap.dedent("""\
            {%- if covariates -%}
            {% for covariate in covariates -%}
            {{ id(index, name) }}({{ loop.index }}).c = [
            {% for value in covariate.values -%}
            {{ ((id(index, name)+"("+(loop.index|string)+").c = {")|length)*" " }}{{ value }}
            {% endfor -%}
            {{ ((id(index, name)+"("+(loop.index|string)+").c = {")|length)*" " }}];
            {{ id(index, name) }}({{ loop.index }}).cname = '{{ covariate.cname }}';
            {{ id(index, name) }}({{ loop.index }}).iCFI = {{ covariate.interactions }};
            {{ id(index, name) }}({{ loop.index }}).iCC = {{ covariate.centering }};
            {% endfor -%}
            {%- else -%}
            {{ id(index, name) }} = struct('c', {}, 'cname', {}, 'iCFI', {}, 'iCC', {});
            {%- endif -%}""")

# Mutliple covariates

class OneSampleTTest(SPMObject):
    def __init__(self, scans):
        super().__init__("spm.stats.factorial_design.des.t1")
        self.scans = scans
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.scans = {
            {% for scan in scans -%}
            {{ ((id(index, name)+".scans = {")|length)*" " }}'{{ scan }}'
            {% endfor -%}
            {{ ((id(index, name)+".scans = {")|length)*" " }}};
            """)
    
    @property
    def file_dep(self):
        return sorted(set(self.scans))

class TwoSamplesTTest(SPMObject):
    def __init__(
            self, scans1, scans2, 
            independence=True, equal_variance=False, grand_mean_scaling=False,
            ancova=False):
        
        super().__init__("spm.stats.factorial_design.des.t2")
        self.scans1 = scans1
        self.scans2 = scans2
        self.independence = independence
        self.equal_variance = equal_variance
        self.grand_mean_scaling = grand_mean_scaling
        self.ancova = ancova
        
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.scans1 = {
            {% for scan in scans1 -%}
            {{ ((id(index, name)+".scans1 = {")|length)*" " }}'{{ scan }}'
            {% endfor -%}
            {{ ((id(index, name)+".scans1 = {")|length)*" " }}};
            {{ id(index, name) }}.scans2 = {
            {% for scan in scans2 -%}
            {{ ((id(index, name)+".scans1 = {")|length)*" " }}'{{ scan }}'
            {% endfor -%}
            {{ ((id(index, name)+".scans1 = {")|length)*" " }}};
            {{ id(index, name) }}.dept = {{ (not independence)|int }};
            {{ id(index, name) }}.variance = {{ (not equal_variance)|int }};
            {{ id(index, name) }}.gmsca = {{ grand_mean_scaling|int }};
            {{ id(index, name) }}.ancova = {{ ancova|int }};
            """)
    
    @property
    def file_dep(self):
        return sorted(set(itertools.chain(self.scans1, self.scans2)))

class PairedTTest(SPMObject):
    def __init__(self, pairs, grand_mean_scaling=False, ancova=False):
        
        super().__init__("spm.stats.factorial_design.des.pt")
        self.pairs = pairs
        self.grand_mean_scaling = grand_mean_scaling
        self.ancova = ancova
        
        self.template = textwrap.dedent("""\
            {% for scan1, scan2 in pairs -%}
            {{ id(index, name) }}.pair({{ loop.index }}) = {
            {{ ((id(index, name)+".pair("+(loop.index|string)+") = {")|length)*" " }}'{{ scan1 }}'
            {{ ((id(index, name)+".pair("+(loop.index|string)+") = {")|length)*" " }}'{{ scan2 }}'
            {{ ((id(index, name)+".pair("+(loop.index|string)+") = {")|length)*" " }}};
            {% endfor -%}
            
            {{ id(index, name) }}.gmsca = {{ grand_mean_scaling|int }};
            {{ id(index, name) }}.ancova = {{ ancova|int }};
            """)
    
    @property
    def file_dep(self):
        return sorted(set(itertools.chain(*self.pairs)))

class ANOVA(SPMObject):
    def __init__(
            self, cells,
            independance=True, equal_variance=False, grand_mean_scaling=False,
            ancova=False):
        
        super().__init__("spm.stats.factorial_design.des.anova")
        self.cells = cells
        self.independance = independance
        self.equal_variance = equal_variance
        self.grand_mean_scaling = grand_mean_scaling
        self.ancova = ancova
        
        self.template = textwrap.dedent("""\
            {% for cell in cells -%}
            {{ id(index, name) }}.icell({{ loop.index }}).scans = {
            {% set padding=((id(index, name)+".icell("+(loop.index|string)+").scans = {")|length)*" " -%}
            {% for scan in cell -%}
            {{ padding }}'{{ scan }}'
            {% endfor -%}
            {{ padding }}};
            {% endfor -%}
            {{ id(index, name) }}.dept = {{ (not independance)|int }};
            {{ id(index, name) }}.variance = {{ (not equal_variance)|int }};
            {{ id(index, name) }}.gmsca = {{ grand_mean_scaling|int }};
            {{ id(index, name) }}.ancova = {{ ancova|int }};
            """)
    
    @property
    def file_dep(self):
        return sorted(set(itertools.chain(*self.cells)))

class FactorialDesign(SPMObject):
    def __init__(
            self, output_directory, design, covariates=None,
            masking=None, global_calculation=None, global_normalization=None):
        
        super().__init__("spm.stats.factorial_design")
        
        self.output_directory = output_directory
        self.design = design
        self.covariates = covariates or Covariates([])
        self.masking = masking or Masking()
        self.global_calculation = global_calculation or GlobalCalculation()
        self.global_normalization = global_normalization or GlobalNormalization()
    
        self.template = textwrap.dedent("""\
            {{ id(index, name) }}.dir = {'{{ output_directory }}'};
            {{ _design }}
            {{ _covariates }}
            {{ id(index, name) }}.multi_cov = struct('files', {}, 'iCFI', {}, 'iCC', {});
            {{ _masking }}
            {{ _global_calculation }}
            {{ _global_normalization }}
            """)
    
    @property
    def spmmat(self):
        return pathlib.Path(self.output_directory)/"SPM.mat"
    
    def get_script(self, index):
        self._design = self.design.get_script(index)
        self._covariates = self.covariates.get_script(index)
        self._masking = self.masking.get_script(index)
        self._global_calculation = self.global_calculation.get_script(index)
        self._global_normalization = self.global_normalization.get_script(index)
        return super().get_script(index)
    
    def _get_targets(self):
        return [self.spmmat]
