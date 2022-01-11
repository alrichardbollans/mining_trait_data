#! /usr/bin/Rscript

# Credit to https://github.com/barnabywalker/latin_america_antimalarials_analysis/blob/main/analysis/01_prepare_names.R

# This script takes an input file of plant data and finds accepted names and ids for the given plants.

# libraries ----
library(here)      # handle file paths
library(dplyr)     # manipulate data
library(readr)     # read text files
library(jsonlite)  # handle json format
library(tidyr)     # reshape data
library(purrr)     # map functions
#library(ape)       # handle phylogenies
#library(rgbif)     # get higher taxonomy from GBIF backbone
library(stringr)   # handle string data
library(kewr)      # request kew data
library(tibble)    # get data into nice tables
#library(progress)  # make nice progress bars



source(here("name_matching_cleaning/helper_functions.R"))
library(optparse)

option_list = list(
    make_option(c("-o", "--out"), type="character",default=NULL,
              help="output file name, defaults to input if not given", metavar="character"),
    make_option(c("-i", "--input"), type="list", default=NULL,
              help="input file name", metavar="character"),
    make_option(c("-c", "--colname"), type="list", default='ID',
              help="name of Name column", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);



# Takes an input csv with a 'Name' column and outputs a csv with an additional accepted name column

# test if there is at least one argument: if not, return an error
if (is.null(opt$input)) {
  stop("Needs input file", call.=FALSE)
}
if (is.null(opt$out)) {
  out_file <- opt$input
} else {
out_file <- opt$out
}
# remotes::install_github("barnabywalker/kewr")
species_csv <- opt$input # Input csv
col_name <- opt$colname # Column name for IDs in dataset (will default to 'ID')

temp_output_folder <- file.path(dirname(species_csv), 'name matching temp outputs')
dir.create(temp_output_folder)

# load species names to query
spp_df = read.csv(species_csv, header=T,sep=",")
species_csv

print(colnames(spp_df))

nested = spp_df %>%
  nest_by(!!sym(col_name))

# get accepted name info for each match
source(here("name_matching_cleaning/helper_functions.R"))

accepted_names <-
  nested %>%
  mutate(info=get_accepted_info(!!sym(col_name))) %>%
  select(-data) %>%
  unnest(cols=c(info)) %>%
  ungroup()

ordered_idx <- match(spp_df[[col_name]],accepted_names[[col_name]])
accepted_name_ordered <- accepted_names[ordered_idx,]

if (! length(accepted_name_ordered[[col_name]]) == length(spp_df[[col_name]])){
  stop("Some submitted items have been lost. This can be caused by incorrect IDs in matching jsons.", call.=FALSE)
}

if (all(accepted_name_ordered[[col_name]] == spp_df[[col_name]])){
  spp_df['Accepted_Name']= accepted_name_ordered$accepted_name
  spp_df['Accepted_ID']= accepted_name_ordered$accepted_id
  spp_df['Accepted_Rank']= accepted_name_ordered$accepted_rank
  spp_df['Accepted_Species']= accepted_name_ordered$accepted_species
  spp_df['Accepted_Species_ID']= accepted_name_ordered$accepted_species_id
  
  write.csv(spp_df, file = out_file,row.names = FALSE)
} else if (!length(accepted_name_ordered$submitted) == length(spp_df[[col_name]])){
  stop("Too many/few accepted names", call.=FALSE)
} else {
  stop("Accepted name order mismatch", call.=FALSE)
}

