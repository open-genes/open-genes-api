from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass



# TODO(cconst8ine)
# Effect of modulation of gene activity on a lifespan
# (This research model will be fully re-worked soon.
# So it's better to mark all class fields as deprecated)
@dataclass
class IncreaseLifespan:
    interventionType: str = Field(title="Intervention type")
    interventionResult: str = Field(title="Intervention result")
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Organism line")
    age: str = Field(title="Age of a model organisms")
    genotype: str = Field(
        title="Genotype",
        description="Genotype designations: \n-/- homozygotes with a weakened gene function, \n+/- heterozygotes with "
                    "a weakened gene function, \n++/++ homozygotes with enhanced gene function, \n++/+ heterozygotes "
                    "with enhanced gene function. "
    )
    valueForMale: str = Field(title="Value for male")
    valueForFemale: str = Field(title="Value for female")
    valueForAll: str = Field(title="Value for all")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")


# Age-related changes in the gene expression or protein activity
@dataclass
class AgeRelatedChangesOfGene:
    changeType: str = Field(title="Changes type")
    sample: str = Field(title="Sample", description="Tissue or cell type the measurement was performed")
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Line")
    ageFrom: str = Field(title="Age of the youngest group of model organisms")
    ageTo: str = Field(title="Age of the oldest group of model organisms")
    valueForMale: str = Field(title="Values in percentage increase or decrease of expression levels for males")
    valueForFemale: str = Field(title="Values in percentage increase or decrease of expression levels for females")
    valueForAll: str = Field(title="Values in percentage increase or decrease of expression levels for both groups")
    measurementType: str = Field(title="A measurement unit for an age of model organisms")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")


@dataclass
class RegulatedGene:
    id: str = Field(title="Gene id in Open Genes database")
    symbol: str = Field(title="Gene symbol (HGNC)")
    name: str = Field(title="Gene name")
    ncbid: str = Field(title="Entrez Gene id")


# Effect of modulation of gene activity on the age-related process
@dataclass
class InterventionToGeneImprovesVitalProcesses:
    geneIntervention: str = Field(title="Method",
                                  description="Any targeted and specific effect that results a change of gene activity")
    vitalProcess: str = Field(title="Process",
                              description="The process, which is amplified or weakened as a result of targeting a gene")
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Organism line")
    interventionResult: str = Field(title="Intervention result")
    age: str = Field(title="Age of a model organisms")
    genotype: str = Field(
        title="Genotype",
        description="Genotype designations: \n-/- homozygotes with a weakened gene function, \n+/- heterozygotes with "
                    "a weakened gene function, \n++/++ homozygotes with enhanced gene function, \n++/+ heterozygotes "
                    "with enhanced gene function. "
    )
    sex: str = Field(title="Biological sex")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")


# Gene product participation in the regulation of genes associated with aging
@dataclass
class ProteinRegulatesOtherGenes:
    """
    Gene product participation in the regulation of genes associated with aging
    """
    proteinActivity: str = Field(title="Protein activity")
    regulationType: str = Field(title="Regulation type")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")
    regulatedGene: RegulatedGene = Field(title="Regulated gene")



# Gene association with accelerated aging in humans
@dataclass
class GeneAssociatedWithProgeriaSyndromes:
    """
    Gene association with accelerated aging in humans.
    """
    progeriaSyndrome: str = Field(title="Progeria syndrome")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")



# Genomic, transcriptomic, and proteomic associations with lifespan/age-related phenotype
@dataclass
class GeneAssociatedWithLongevityEffects:
    """
    Genomic, transcriptomic, and proteomic associations with lifespan/age-related phenotype.
    """
    longevityEffect: str = Field(title="A trait associated with polymorphism")
    allelicPolymorphism: str = Field(title="Allelic polymorphism",
                                     description="SNP id or another or another designation for gene polymorphism")
    sex: str = Field(title="Biological sex")
    allelicVariant: str = Field(title="Allelic variant",
                                description="Polymorphic gene variant associated with the trait")
    modelOrganism: str = Field(title="Model organism")
    changeType: str = Field(title="Characteristics of the transcriptome / proteome")
    dataType: str = Field(title="Data type")
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")


# Other evidence for the gene's association with aging
@dataclass
class AdditionalEvidence:
    """
    Other evidence for the gene's association with aging.
    """
    doi: str = Field(title="Publication id in DOI format")
    pmid: str = Field(title="Publication id in PMC/PMID format")
    comment: str = Field(title="Additional description")


@dataclass
class Researches:
    increaseLifespan: List[IncreaseLifespan] = Field(
        title="Effect of modulation of gene activity on a lifespan"
    )
    ageRelatedChangesOfGene: Optional[List[AgeRelatedChangesOfGene]] = Field(
        title="Age-related changes in the gene expression or protein activity"
    )
    interventionToGeneImprovesVitalProcesses: List[InterventionToGeneImprovesVitalProcesses] = Field(
        title="Effect of modulation of gene activity on the age-related process"
    )
    proteinRegulatesOtherGenes: Optional[List[ProteinRegulatesOtherGenes]] = Field(
        title="Gene product participation in the regulation of genes associated with aging"
    )
    geneAssociatedWithProgeriaSyndromes: Optional[List[GeneAssociatedWithProgeriaSyndromes]] = Field(
        title="Gene association with accelerated aging in humans"
    )
    geneAssociatedWithLongevityEffects: Optional[List[GeneAssociatedWithLongevityEffects]] = Field(
        title="Genomic, transcriptomic, and proteomic associations with lifespan/age-related phenotype"
    )
    additionalEvidences: Optional[List[AdditionalEvidence]] = Field(
        title="Other evidence for the gene's association with aging"
    )
