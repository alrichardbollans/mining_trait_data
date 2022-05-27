#install.packages("Rcpp")
#remotes::install_github("rspatial/terra")
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

source(here(file.path('helper functions','queryGBIF.R')))
source(here('configs.R'))
source(file.path(input_dir, 'gbif.secrets'))

# load species names to querry in GBIF
taxa_df = read.csv(taxa_csv, sep=",")
taxa_list = taxa_df$taxon_name

# Best to download for all taxa in one go
# Reboot before download as stored tmp files can interfere
species_occurences <- queryGBIF(species_name=taxa_list, # vector of species names
                    user=username,
                    email=email,
                    pwd=password,
                    rank='species', kingdom='Plantae',
                    gbif_download_dir = temp_output_dir, #path to directory where to save GBIF raw occurrence data
                    check_output=temp_output_dir)# path to directory where to save info about the query to GBIF where, username, email and password are your GBIF credentials

data.table::setkey(species_occurences,"species")

if (file.exists(gbif_occ_dir)) {
  
  cat("The gbif_occ_dir already exists")
  
} else {
  
  dir.create(gbif_occ_dir)
  
}

for(k in unique(species_occurences [["species"]])){
  
  sp <- gsub(" ","_", k)
  
  write.csv(species_occurences[k], file.path(gbif_occ_dir ,paste0(sp,'.csv')), row.names=FALSE)
  
}


