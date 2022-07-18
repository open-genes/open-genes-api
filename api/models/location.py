from models import *
from pydantic import BaseModel


class Exon(BaseModel):
    id: int | None
    begin: int | None
    end: int | None
    order: int | None

    _select = {
        'id': 'transcript_exon.id',
        'transcript_id': 'transcripts.id',
        'begin': 'transcript_exon.begin',
        'end': 'transcript_exon.end',
        'order': 'transcript_exon.ord',
    }

    _from = """
from transcripts
left join transcript_exon on transcript_exon.transcript_id=transcripts.id
    """


class Transcript(BaseModel):
    id: int | None
    exons: List[Exon]
    accVersion: str | None
    name: str | None
    length: int | None
    genomicRangeAccVersion: str | None
    genomicRangeBegin: int | None
    genomicRangeEnd: int | None
    genomicRangeOrientation: int | None

    _select = {
        'id': 'gene_transcript.id',
        'gene_id': 'gene.id',
        'accVersion': 'gene_transcript.acc_version',
        'name': 'gene_transcript.name',
        'length': 'gene_transcript.length',
        'genomicRangeAccVersion': 'gene_transcript.genomic_range_acc_version',
        'genomicRangeBegin': 'gene_transcript.genomic_range_begin',
        'genomicRangeEnd': 'gene_transcript.genomic_range_end',
        'genomicRangeOrientation': 'gene_transcript.genomic_range_orientation',
    }

    _from = """
from gene
left join gene_transcript on gene_transcript.gene_id=gene.id
    """


class Location(BaseModel):
    transcripts: List[Transcript] | None
    locationStart: int | None
    locationEnd: int | None
    band: str | None
    orientation: str | None
    accPromoter: str | None
    accOrf: str | None
    accCds: str | None
    chromosome: int | None

    _select = {
        'locationStart': 'gene.locationStart',
        'locationEnd': 'gene.locationEnd',
        'band': 'gene.band',
        'orientation': 'gene.orientation',
        'accPromoter': 'gene.accPromoter',
        'accOrf': 'gene.accOrf',
        'accCds': 'gene.accCds',
        'chromosome': 'gene.chromosome',
    }
