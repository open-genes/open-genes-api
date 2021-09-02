class Gene(BaseModel):
    id: int
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
    isHidden: int
    expressionChange: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    family_phylum_id: Optional[int] = None
    protein_complex_ru: Optional[str] = None
    protein_complex_en: Optional[str] = None
    taxon_id: Optional[int] = None
    ensembl: Optional[str] = None
    human_protein_atlas: Optional[str] = None
    ncbi_summary_ru: Optional[str] = None
    ncbi_summary_en: Optional[str] = None
    source: Optional[str] = None
    og_summary_en: Optional[str] = None
    og_summary_ru: Optional[str] = None
    methylation_horvath: Optional[int] = None
    phylum_id: Optional[int] = None


