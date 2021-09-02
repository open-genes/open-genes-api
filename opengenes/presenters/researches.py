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


class Researches(BaseModel):
    increaseLifespan: List[IncreaseLifespan]
    geneAssociatedWithProgeriaSyndromes: Optional[List]
    geneAssociatedWithLongevityEffects: Optional[List]
    ageRelatedChangesOfGene: Optional[List]
    interventionToGeneImprovesVitalProcesses: List[InterventionToGeneImprovesVitalProcesses]
    proteinRegulatesOtherGenes: Optional[List]
    additionalEvidences: Optional[List]
