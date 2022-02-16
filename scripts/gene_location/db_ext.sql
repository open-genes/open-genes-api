-- up
-- ------------------------------------------------------------------
CREATE TABLE worker_state
(
    name  TEXT,
    state TEXT
);

CREATE UNIQUE INDEX uin_worker_state
    ON worker_state (name);

-- ------------------------------------------------------------------
ALTER TABLE gene
    ADD COLUMN hgnc_id TEXT;

ALTER TABLE gene
    ADD COLUMN uniprot_id TEXT;

-- gene locus group -------------------------------------------------
CREATE TABLE gene_locus_group
(
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT
);

CREATE UNIQUE INDEX uin_gene_locus_group_name
    ON gene_locus_group (name);

ALTER TABLE gene
    ADD COLUMN locus_group INTEGER;


-- gene group -------------------------------------------------
CREATE TABLE gene_group
(
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT
);

CREATE UNIQUE INDEX uin_gene_group_name
    ON gene_group (name);

ALTER TABLE gene
    ADD COLUMN gene_group INTEGER;


-- gene transcript -------------------------------------------------
CREATE TABLE gene_transcript
(
    id                        INT AUTO_INCREMENT PRIMARY KEY,
    gene_id                   INT REFERENCES gene (id) ON DELETE CASCADE,
    acc_version               TEXT NOT NULL,
    name                      TEXT NOT NULL,
    length                    INT,
    genomic_range_acc_version TEXT NOT NULL,
    genomic_range_begin       INT,
    genomic_range_end         INT,
    genomic_range_orientation INT
);


CREATE INDEX in_gene_transcript_gene_id
    ON gene_transcript (gene_id);

-- transcript exon -------------------------------------------------
CREATE TABLE transcript_exon
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    transcript_id INT REFERENCES gene_transcript (id) ON DELETE CASCADE,
    begin         INT,
    end           INT,
    ord           INT
);

CREATE INDEX in_transcript_exon_transcript_id
    ON gene_transcript (id);

-- down
ALTER TABLE gene
    DROP COLUMN IF EXISTS hgnc_id;
ALTER TABLE gene
    DROP COLUMN IF EXISTS uniprot_id;
ALTER TABLE gene
    DROP COLUMN IF EXISTS locus_group;
ALTER TABLE gene
    DROP COLUMN IF EXISTS gene_group;
DROP TABLE IF EXISTS gene_locus_group;
DROP TABLE IF EXISTS gene_group;
DROP TABLE IF EXISTS transcript_exon;
DROP TABLE IF EXISTS gene_transcript;
DROP TABLE IF EXISTS worker_state;
