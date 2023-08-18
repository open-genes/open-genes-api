Open Genes is a non-commercial public service for biologists — a biological database of human genes associated with aging and lifespan.

Open Genes API is a RESTful API that allows for programmatic access to the Open Genes database:  The API provides GET endpoints for accessing data on genes associated with aging and longevity as well as detailed structured data for each experiment binding the gene and aging: For example, we provide up to 40 parameters for each lifespan experiment: Our API provides basic and additional data for each gene, such as gene evolution, associated diseases, hallmarks of aging linked with genes, and protein functions: It also includes various parameters for filtering and sorting: Our goal is to stay objective and precise while connecting a particular gene and human aging and to keep the gene selection criteria transparent: We distinguished six types of studies and 12 criteria for adding genes to the Open Genes database: Genes were divided into highest, high, moderate, low, and lowest confidence level groups based on the type of data supporting the link between the gene and aging: 
Open Genes API is a part of Open Genes infrastructure that includes other backend services, a data management application for biologists, and a frontend application.
Complete interactive API documentation in Swagger (OpenAPI) format can be found at https://open-genes.org/api/docs.

## What's Changed

### Release v1.1.1
* OG-923: Update CHANGELOG.md
* OG-923: Add CONTRIBUTING.md
* OG-923: Add script for changelog generation

### Release v1.1.0
* bugfix: Fixed issue for hallmarks of aging which was caused by an empty field in API response by @psnewbee #150
* OG-957: Fix pandas import and add a check if hallmarks are set for gene by @psnewbee #123
* OG-957: Fix filter for byConservativeIn parameter by @psnewbee #121
* OG-949: Output manually bound hallmarks of aging by @psnewbee #119
* OG-910: Fix bySpecies filter in studies by @psnewbee #111
* Output distinct hallmarks of aging entries in the API response by @const8ine #117
* Fix query causing duplicated hallmarks of aging in response by @const8ine #108
* OG-936: Remove a fixer for the measurement method field, fix empty response by @Anthony1128 #106
* Add updated datasets with missing experiments for upload by @const8ine #107
* Update hallmarks of aging dataset by @const8ine #120
* Update confidence levels dataset by @const8ine #143
* bugfix: Fixed issue which was caused by empty agingMechanisms field in response by @psnewbee
* OG-346: Fix missing methods in CalorieExperimentDAO by @Anthony1128 and @const8ine #141.
* Added filter by symbol in gene/search API endpoint by @Anthony1128
* OG-885: Set up API response caching by @Anthony1128 #94
* OG-863: Change config for binding GO-terms with hallmarks by @const8ine #70
* OG-909: Duplicates scanner by @Anthony1128 #101
* bugfix: Fix condition for the aliases splitting by @Anthony1128 #100
* OG-908: Change confidenceLevel field format by @Anthony1128 #99
* OG-892: confidenceLevel output field update by @const8ine #98
* OG-906: expression-change-human-mrna dataset by @const8ine #97
* bugfix: Fix values trimming in longevity associations dataset upload script by @Anthony1128 #96
* OG-906: Script for uploading data from expression-change-human-mrna dataset by @Anthony1128 #95
* OG-809: Script for uploading data from longevity associations dataset by @Anthony1128 #90
* OG-882: SQL injection fix by @Anthony1128 #82
* bugfix: Fix SQL query for filtering the studies on the association of gene variants or expression levels with longevity by @Anthony1128 #92
* OG-889: Confidence level in api/gene/search API endpoint response by @Anthony1128 #87
* OG-901: Study filter placeholder by @Anthony1128 #88
* OG-898: Fix typing for AgeRelatedChangeOfGene model by @const8ine #84
* OG-887: Add filters to lifespan-change API endpoint by @psnewbee #83
* OG-877: Add isHidden param to api/diet by @Anthony1128 #78
* OG-881: gene/suggestions API endpoint suggestHidden param by @Anthony1128 #81
* OG-873: Add linter by @Anthony1128 #77
* OG-838: Fix filter logic by @Anthony1128 #74
* OG-851: Always output tissueSpecificPromoter field in response by @const8ine #64
* OG-589: Fix absent 'significance' field in pink form by @const8ine #66
* OG-589: Add new fields to studies on the association of gene variants or expression levels with longevity by @tinymage #57
* OG-589: Delete modelOrganism field from GeneAssociatedWithLongevityEffect response by @tinymage #54
* OG-763: Add Wormbase orthologs parser by @zheld #55
* bugfix: Fix empty HPA issue by @kergma #53
* bugfix: Fix empty terms that broke a single gene response by @kergma #52
* bugfix: Fix orthologs parser for studies on calorie restriction diets by @lannoyy #28
* OG-376: Fix response for studies on age-related changes in gene expression, methylation or protein activity by @kergma #50
* OG-617: Add bySuggestions parameter to api/gene/search API endpoint by @zheld #36
* OG-617: Implement modular models approach for API by @kergma #36

## Contributors
* @imhelle made their first contribution #10
* @dglubokov made their first contribution #1
* @kergma made their first contribution #27
* @lannoyy made their first contribution #3
* @zheld made their first contribution #31
* @tinymage made their first contribution #49
* @const8ine made their first contribution #102



