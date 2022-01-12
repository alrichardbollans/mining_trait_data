# From https://github.com/barnabywalker/latin_america_antimalarials_analysis/blob/7ec2ffa320cf43cd085e05ee733591d6e367ca63/R/helper_functions.R

# data request functions ----

#' Utility to check if a taxon name is in a lookup of IDs.
check_id <- function(name, id) {
  if (name %in% names(missing_names)) {
    id <- missing_names[[name]]
  }
  
  id
}

#' Utility to get accepted name information for an IPNI ID.
get_accepted_info <- function(ipni_id) {

  # empty table to return if nothing comes back
  info <- tibble(
    status=NA_character_,
    accepted_id=NA_character_,
    accepted_name=NA_character_,
    accepted_authors=NA_character_,
    accepted_rank=NA_character_,
    accepted_species=NA_character_,
    accepted_species_id=NA_character_
  )
  print(ipni_id)
  # lookup_wcvp breaks when taxon is family.
  #family_ids = c('30000032-2','319342-2', '30032120-2')
  if (is.na(ipni_id) || ipni_id == ""){
    return(list(info))
  }
  
  # get WCVP entry for ID
  r <- tryCatch({
    kewr::lookup_wcvp(ipni_id)
  },
  error = function(e) {
    list(info)
  })
  
  if (is.null(r$status) ){
    return(list(info))
  }
  
  
  info$status <- r$status
  
  # extract info about accepted name
  if (info$status %in% c("accepted", "unplaced")) {
    info$accepted_id <- r$id
    info$accepted_name <- r$name
    info$accepted_authors <- r$author
    info$accepted_rank <- r$rank
  } else {
    info$accepted_id <- r$accepted$id
    info$accepted_name <- r$accepted$name
    info$accepted_authors <- r$accepted$authors
    info$accepted_rank <- r$accepted$rank
  }

  if (! "accepted_rank" %in% colnames(info)) {
        return(list(info))
  }

  # handle infraspecifics by getting the parent name
  if (info$accepted_rank %in% c("Variety", "Subspecies")) {
    r <- kewr::lookup_wcvp(info$accepted_id)
    info$accepted_species <- r$parent$name
    info$accepted_species_id <- r$parent$id
  } else if (info$accepted_rank == "Species") {
    info$accepted_species <- info$accepted_name
    info$accepted_species_id <- info$accepted_id
  }
  
  # wrap in a list to make it interface with dplyr's rowwise nicely
  list(info)
}






