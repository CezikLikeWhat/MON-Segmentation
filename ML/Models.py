from enum import Enum


class Models(str, Enum):
    CLINICAL_CT_ORGANS = 'clin_ct_organs'
    CLINICAL_CT_LUNGS = 'clin_ct_lungs'
    CLINICAL_PET_TUMOR = 'clin_pt_fdg_tumor'
    CLINICAL_CT_BODY = 'clin_ct_body'
    CLINICAL_CT_RIBS = 'clin_ct_ribs'
    CLINICAL_CT_MUSCLES = 'clin_ct_muscles'
    CLINICAL_CT_PERIPHERAL_BONES = 'clin_ct_peripheral_bones'
    CLINICAL_CT_FAT = 'clin_ct_fat'
    CLINICAL_CT_VERTEBRAE = 'clin_ct_vertebrae'
    CLINICAL_CT_CARDIAC = 'clin_ct_cardiac'
    CLINICAL_CT_DIGESTIVE = 'clin_ct_digestive'
    PRECLINICAL_MR_ALL = 'preclin_mr_all'

    @staticmethod
    def get_all_options():
        return [m.value for m in Models]
