#! /usr/bin/Rscript
# Credit to https://github.com/barnabywalker/
library(dplyr)
library(optparse)
# install.packages('remotes')
#remotes::install_github("barnabywalker/kewr")
library(kewr)

# May want extra options for different powo filters.
# May also want to hand verify that hits are accurate
option_list = list(
    make_option(c("-o", "--out"), type="character", default="powo_search_out.csv",
              help="output file name [default= %default]", metavar="character"),
    make_option(c("-s", "--searchterms"), type="list", default=NULL,
              help="list of searchterms to search for. Pass as e.g. \'poisonous,poison\'", metavar="character")
);

opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);

if (is.null(opt$searchterms)) {
  stop("list of search terms must be supplied", call.=FALSE)
}

if (is.null(opt$out)) {
  stop("output csv must be supplied", call.=FALSE)
}
# I think the list can be passed alone
out_csv = opt$out
split_list <- strsplit(opt$searchterms, ",")
searchterms <- split_list[[1]]

new = c()

search_query <- function(qry,dataf){
  # Appearance, fruit are in characteristic
    r <- search_powo(qry, filters=c("species"), limit = 10000)
    tr = tidy(r)
    # Remove imgs and synonymOf column
    if("images" %in% colnames(tr)){
      tr <- tr %>%
        select(-images)
    }
    if("synonymOf" %in% colnames(tr)){
      tr <- tr %>%
        select(-synonymOf)
    }
    
    dataout <- rbind(tr,dataf)
    return(dataout)
}
for(st in searchterms){
  # Appearance, fruit are in characteristic, others may be but I'm not sure
  query <- list('characteristic'=st)
  new <- search_query(query,new)

  query <- list('summary'=st)
  new <- search_query(query,new)

  query <- list('flower'=st)
  new <- search_query(query,new)

  query <- list('leaf'=st)
  new <- search_query(query,new)

  query <- list('inflorescence'=st)
  new <- search_query(query,new)

  query <- list('seed'=st)
  new <- search_query(query,new)

  query <- list('cloning'=st)
  new <- search_query(query,new)

  query <- list('use'=st)
  new <- search_query(query,new)

  query <- list('distribution'=st)
  new <- search_query(query,new)
}

if(! nrow(new)== 0){

  write.csv(new, file = out_csv)
  
} else{
  print("No hits")
}

