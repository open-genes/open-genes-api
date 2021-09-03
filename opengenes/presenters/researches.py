from typing import List, Optional

from pydantic import BaseModel, Field


class IncreaseLifespan(BaseModel):
    interventionType: str = Field(title="Intervention type")
    interventionResult: str = Field(title="Intervention result")
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Organism line")
    age: str
    genotype: str
    valueForMale: str = Field(title="Value for male")
    valueForFemale: str = Field(title="Value for female")
    valueForAll: str = Field(title="Value for all")
    doi: str
    pmid: str
    comment: str


class GeneAssociatedWithProgeriaSyndromes(BaseModel):
    progeriaSyndrome: str = Field(title="Progeria syndrome")
    doi: str
    pmid: str
    comment: str


class GeneAssociatedWithLongevityEffects(BaseModel):
    longevityEffect: str = Field(title="Longevity effect")
    allelicPolymorphism: str = Field(title="Allelic polymorphism")
    sex: str
    allelicVariant: str = Field(title="Allelic variant")
    modelOrganism: str = Field(title="Model organism")
    changeType: str = Field(title="Change type")
    dataType: str = Field(title="Data type")
    doi: str
    pmid: str
    comment: str


class AgeRelatedChangesOfGene(BaseModel):
    changeType: str = Field(title="Change type")
    sample: str
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Organism line")
    ageFrom: str = Field(title="Age from")
    ageTo: str = Field(title="Age to")
    valueForMale: str = Field(title="Value for male")
    valueForFemale: str = Field(title="Value for female")
    valueForAll: str = Field(title="Value for all")
    measurementType: str = Field(title="Measurement type")
    doi: str
    pmid: str
    comment: str


class RegulatedGene(BaseModel):
    id: str
    symbol: str
    name: str
    ncbid: str


class ProteinRegulatesOtherGenes(BaseModel):
    proteinActivity: str = Field(title="Protein activity")
    regulationType: str = Field(title="Regulation type")
    doi: str
    pmid: str
    comment: str
    regulatedGene: RegulatedGene = Field(title="Regulated gene")


class InterventionToGeneImprovesVitalProcesses(BaseModel):
    geneIntervention: str = Field(title="Gene intervention")
    vitalProcess: str = Field(title="Vital process")
    modelOrganism: str = Field(title="Model organism")
    organismLine: str = Field(title="Organism line")
    interventionResult: str = Field(title="Intervention result")
    age: str
    genotype: str
    sex: str
    doi: str
    pmid: str
    comment: str


class AdditionalEvidence(BaseModel):
    doi: str
    pmid: str
    comment: str


class Researches(BaseModel):
    increaseLifespan: List[IncreaseLifespan] = Field(title="Increase lifespan")
    geneAssociatedWithProgeriaSyndromes: Optional[List[GeneAssociatedWithProgeriaSyndromes]] = Field(
        title="Gene associated with progeria syndromes"
    )
    geneAssociatedWithLongevityEffects: Optional[List[GeneAssociatedWithLongevityEffects]] = Field(
        title="Gene associated with longevity syndromes"
    )
    ageRelatedChangesOfGene: Optional[List[AgeRelatedChangesOfGene]] = Field(
        title="Age related changes of gene"
    )
    interventionToGeneImprovesVitalProcesses: List[InterventionToGeneImprovesVitalProcesses] = Field(
        title="Intervention to gene improves vital processes"
    )
    proteinRegulatesOtherGenes: Optional[List[ProteinRegulatesOtherGenes]] = Field(
        title="Protein regulates other genes"
    )
    additionalEvidences: Optional[List[AdditionalEvidence]] = Field(
        title="Additional evidences"
    )
