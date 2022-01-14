#! /usr/bin/Rscript

# Credit to https://github.com/barnabywalker/latin_america_antimalarials_analysis/blob/main/analysis/01_prepare_names.R

# This script takes an input file of plant data and finds accepted names and ids for the given plants.
# Takes an input csv with a 'Name' column and outputs a csv with an additional accepted info columns

# libraries ----
library(here)      # handle file paths
library(dplyr)     # manipulate data
library(readr)     # read text files
library(jsonlite)  # handle json format
library(tidyr)     # reshape data
library(purrr)     # map functions
library(stringr)   # handle string data
library(kewr)      # request kew data
library(tibble)    # get data into nice tables


library(optparse)

option_list = list(
    make_option(c("-o", "--out"), type="character",default=NULL,
              help="output file name", metavar="character"),
    make_option(c("-i", "--input"), type="list", default=NULL,
              help="input file name", metavar="character"),
    make_option(c("-c", "--colname"), type="list", default='Name',
              help="name of Name column", metavar="character"),
    make_option(c("-p", "--packagepath"), type="character",
              help="Path to current package/script", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$input)) {
  stop("Needs input file", call.=FALSE)
}
if (is.null(opt$out)) {
  stop("Needs output file", call.=FALSE)
}
# remotes::install_github("barnabywalker/kewr")
species_csv <- opt$input # Input csv
out_file <- opt$out
col_name <- opt$colname # Column name for plant names in dataset (will default to 'Name')
path_here <- opt$packagepath

print(path_here)

source(file.path(path_here,"helper_functions.R"))

temp_output_folder <- file.path(dirname(species_csv), 'name matching temp outputs')
dir.create(temp_output_folder)

# load species names to query
spp_df = read.csv(species_csv, header=T,sep=",")
species_csv

spp = spp_df[[col_name]]
spp = as.character(spp)


full_matches <- kewr::match_knms(spp)
full_matches = kewr::tidy(full_matches)
# 'full_matches'
# full_matches

# show the taxa with no matches
unmatched <- dplyr::filter(full_matches, ! matched)
# These are names initially not given any matching by match_knms function
# 'unmatched'
# unmatched

# resolve unmatched names using a manual matching file
missing_names <- jsonlite::read_json(file.path(path_here,"matching data/name_match_missing.json"))

# Uses missing_names via check_id function (from helper functions)
matched_names <-
 full_matches %>%
 mutate(ipni_id=purrr::map2_chr(submitted, ipni_id, check_id))

# show the taxa with multiple matches
multiple_matches <-
  full_matches %>%
  add_count(submitted) %>%
  filter(n > 1)

'multiple_matches'
multiple_matches

# resolve multiple matches with a manual matching file
# Some multiple matches need resolving to unaccepted ids first here and then correcting in mannual match correction later.
match_resolutions <- jsonlite::read_json(file.path(path_here,"matching data/name_match_multiples.json"))


matched_names <-
  matched_names %>%
  filter((! submitted %in% names(match_resolutions))|ipni_id %in% match_resolutions)

unresolved_matched_multiples <-
    multiple_matches %>%
    filter(!((submitted %in% names(match_resolutions))|ipni_id %in% match_resolutions))

incorrect_ids <-
  multiple_matches %>%
  filter(!(submitted %in% matched_names$submitted))

if (! length(incorrect_ids$submitted) == 0){
  print('incorrect_ids')
  print(incorrect_ids)
  
  incorrect_ids_file = paste(temp_output_folder,"/incorrect",basename(species_csv),sep="")
  incorrect_ids %>%
    write_csv(here(incorrect_ids_file))
  
  stop("Some submitted items have been lost. This can be caused by incorrect IDs in matching jsons.", call.=FALSE)
}

'unresolved multiples matches'
unresolved_matched_multiples
unresolved_matched_multiples_file = paste(temp_output_folder,"/unresolved_multiple_matches_",basename(species_csv),sep="")
unresolved_matched_multiples %>%
    write_csv(here(unresolved_matched_multiples_file))

# manually fix a couple matches
match_correction <- jsonlite::read_json(file.path(path_here,"matching data/manual_match_correction.json"))

matched_names <-
  matched_names %>%
  mutate(ipni_id=recode(ipni_id, !!! match_correction),
        matched_record=ifelse(ipni_id %in% names(match_correction),
                              NA_character_,
                             matched_record))
# 'matched names'
# matched_names


nested = matched_names %>%
  nest_by(submitted, match_id=ipni_id)

# get accepted name info for each match
accepted_names <-
   nested %>%
  mutate(info=get_accepted_info(match_id)) %>%
  select(-data) %>%
  unnest(cols=c(info)) %>%
  ungroup()

# save for posterity
sv_file = paste(temp_output_folder,"/",basename(species_csv),sep="")
accepted_names %>%
  write_csv(here(sv_file))

# Check unmatched_names
unmatched_csv_file = paste(temp_output_folder,"/unmatched_",basename(species_csv),sep="")
unmatched_data = accepted_names[is.na(accepted_names$accepted_name), ]
write.csv(unmatched_data,here(unmatched_csv_file))
if (nrow(unmatched_data)>0) {
'unmatched_names'
    unmatched_data

  warning("Not all names matched --- check temp outputs", call.=FALSE)
}


# First reorder accepted_names to match input dataframe
ordered_idx <- match(spp_df[[col_name]],accepted_names$submitted)
accepted_name_ordered <- accepted_names[ordered_idx,]

if (! length(accepted_name_ordered$submitted) == length(spp_df[[col_name]])){
  stop("Some submitted items have been lost. This can be caused by incorrect IDs in matching jsons.", call.=FALSE)
}

if (all(accepted_name_ordered$submitted == spp_df[[col_name]])){
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
