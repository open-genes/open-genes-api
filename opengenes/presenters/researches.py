from typing import List, Optional

from pydantic import BaseModel


class IncreaseLifespan(BaseModel):
    interventionType: str
    interventionResult: str
    modelOrganism: str
    organismLine: str
    age: str
    genotype: str
    valueForMale: str
    valueForFemale: str
    valueForAll: str
    doi: str
    pmid: str
    comment: str


class GeneAssociatedWithProgeriaSyndromes(BaseModel):
    progeriaSyndrome: str
    doi: str
    pmid: str
    comment: str


class GeneAssociatedWithLongevityEffects(BaseModel):
    longevityEffect: str
    allelicPolymorphism: str
    sex: str
    allelicVariant: str
    modelOrganism: str
    changeType: str
    dataType: str
    doi: str
    pmid: str
    comment: str


class AgeRelatedChangesOfGene(BaseModel):
    changeType: str
    sample: str
    modelOrganism: str
    organismLine: str
    ageFrom: str
    ageTo: str
    valueForMale: str
    valueForFemale: str
    valueForAll: str
    measurementType: str
    doi: str
    pmid: str
    comment: str


class RegulatedGene(BaseModel):
    id: str
    symbol: str
    name: str
    ncbid: str


class ProteinRegulatesOtherGenes(BaseModel):
    proteinActivity: str
    regulationType: str
    doi: str
    pmid: str
    comment: str
    regulatedGene: RegulatedGene


class InterventionToGeneImprovesVitalProcesses(BaseModel):
    geneIntervention: str
    vitalProcess: str
    modelOrganism: str
    organismLine: str
    interventionResult: str
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
    increaseLifespan: List[IncreaseLifespan]
    geneAssociatedWithProgeriaSyndromes: Optional[List[GeneAssociatedWithProgeriaSyndromes]]
    geneAssociatedWithLongevityEffects: Optional[List[GeneAssociatedWithLongevityEffects]]
    ageRelatedChangesOfGene: Optional[List[AgeRelatedChangesOfGene]]
    interventionToGeneImprovesVitalProcesses: List[InterventionToGeneImprovesVitalProcesses]
    proteinRegulatesOtherGenes: Optional[List[ProteinRegulatesOtherGenes]]
    additionalEvidences: Optional[List[AdditionalEvidence]]
