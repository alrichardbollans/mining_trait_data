library(data.table)
library(occCite)
library(stringr)
library(CoordinateCleaner)
library(dplyr)
library(raster)
library(rgbif)
library(taxize)
library(countrycode)
library(doParallel)
library(foreach)
library(geojsonio)
library(here)
#devtools::install_local(file.path(here(),'TDWG_0.0.0.9000','TDWG'), dep=T)
library(TDWG)

source(here(file.path('helper functions','cleanOcc.R')))
source(here('configs.R'))


# This function eats RAM. Possibly better to iterate over files in gbif_occ_dir
cleaned_occ <- cleanOcc(species_occ = gbif_occ_dir,# path to folder (or file) where csv species occurrence files to clean are saved
                           cutoff_year = 1945,
                           cutoff_coord_uncertainty = 20000,
                           buffer_cent = 1000,
                           buffer_cap = 10000,
                           buffer_inst = 1000,
                           buffer_gbif_HQ = 1000,
                           output_dir = temp_clean_output_dir, # path to directory where to save cleaned occurrence data
                           rscript = here(file.path('helper functions','occCleaning.R')),
                           use_TDWG = TRUE, # enable/disable cleaning by TDWG regions
                           mc_cores = 7)                   

# Repackage into single csv
# Get cleaned occurence files
spp_occ_files = list.files(temp_clean_output_dir, 
                           pattern = '*.csv$', full.names = T)

# Create a dataframe containing cleaned occurences
clean_taxa_df = read.csv(spp_occ_files[1])
for(f in tail(spp_occ_files, -1)){
  f_df = read.csv(f)
  clean_taxa_df = rbind(clean_taxa_df,f_df)
}

#Output to csv
write.csv(clean_taxa_df, cleaned_taxa_output_csv)

