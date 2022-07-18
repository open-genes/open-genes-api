from typing import Optional

from pydantic import BaseModel

# TODO(dmtgk): Add all entities.
# TODO(dmtgk): Validate schema with team.


class Age(BaseModel):
    # id: int
    name_phylo: Optional[str] = None
    name_mya: Optional[str] = None
    order: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class Taxon(BaseModel):
    # id: int
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class Gene(BaseModel):
    # id: int
    isHidden: Optional[int] = None
    symbol: Optional[str] = None
    aliases: Optional[str] = None
    name: Optional[str] = None
    ncbi_id: Optional[int] = None
    uniprot: Optional[str] = None
    why: Optional[str] = None
    band: Optional[str] = None
    locationStart: Optional[int] = None
    locationEnd: Optional[int] = None
    orientation: Optional[int] = None
    accPromoter: Optional[str] = None
    accOrf: Optional[str] = None
    accCds: Optional[str] = None
    references: Optional[str] = None
    orthologs: Optional[str] = None
    commentEvolution: Optional[str] = None
    commentFunction: Optional[str] = None
    commentCause: Optional[str] = None
    commentAging: Optional[str] = None
    commentEvolutionEN: Optional[str] = None
    commentFunctionEN: Optional[str] = None
    commentAgingEN: Optional[str] = None
    commentsReferenceLinks: Optional[str] = None
    rating: Optional[int] = None
    expressionChange: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    protein_complex_ru: Optional[str] = None
    protein_complex_en: Optional[str] = None
    ensembl: Optional[str] = None
    human_protein_atlas: Optional[str] = None
    ncbi_summary_ru: Optional[str] = None
    ncbi_summary_en: Optional[str] = None
    source: Optional[str] = None
    og_summary_en: Optional[str] = None
    og_summary_ru: Optional[str] = None
    methylation_horvath: Optional[int] = None
    uniprot_summary_en: Optional[str] = None
    uniprot_summary_ru: Optional[str] = None

    age: Optional[Age] = None
    taxon: Optional[Taxon] = None


class Disease(BaseModel):
    # id: int
    omim_id: Optional[int] = None
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    icd_code: Optional[str] = None
    parent_icd_code: Optional[str] = None
    icd_name_en: Optional[str] = None
    icd_name_ru: Optional[str] = None
    icd_code_visible: Optional[str] = None


class Source(BaseModel):
    # id: int
    name: Optional[str] = None


class GeneToSource(BaseModel):
    gene_id: Optional[int] = None
    source_id: Optional[int] = None


class CalorieRestrictionExperiment(BaseModel):
    # id: int
    gene_id: Optional[int] = None
    p_val: Optional[str] = None
    result: Optional[str] = None
    measurement_method_id: Optional[int] = None
    expression_evaluation_by_id: Optional[int] = None
    restriction_percent: Optional[float] = None
    restriction_time: Optional[int] = None
    restriction_time_unit_id: Optional[int] = None
    age: Optional[str] = None
    age_time_unit_id: Optional[int] = None
    model_organism_id: Optional[int] = None
    strain_id: Optional[int] = None
    organism_sex_id: Optional[int] = None
    tissue_id: Optional[int] = None
    isoform_id: Optional[int] = None
    experiment_number: Optional[str] = None
    expression_change_log_fc: Optional[str] = None
    expression_change_percent: Optional[str] = None
    doi: Optional[str] = None


class GeneTranscript(BaseModel):
    gene_id: Optional[int] = None
    acc_version: Optional[str] = None
    name: Optional[str] = None
    length: Optional[int] = None
    genomic_range_acc_version: Optional[str] = None
    genomic_range_begin: Optional[int] = None
    genomic_range_end: Optional[int] = None
    genomic_range_orientation: Optional[int] = None


class GeneTranscriptExon(BaseModel):
    transcript_id: Optional[int] = None
    begin: Optional[int] = None
    end: Optional[int] = None
    ord: Optional[int] = None
