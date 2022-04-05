library(raster)

import_raster <- function(filename){
  str_name<-paste('/home/atp/Downloads/rasters/',filename,sep='')
  imported_raster=raster(str_name)
  return(imported_raster)
}

append_var_to_df <- function(df,var_name){
  x = import_raster(var_name)
  var_values = data.frame(extract(stack(x), df[, c("decimalLongitude", "decimalLatitude")]))
  return(cbind(df, var_values))
}


# Get dataframe containing cleaned occurences
species_df = read.csv(file.path('inputs','cleaned_species_occurences.csv'))
bioclim_df <- species_df

bioclim_df<-append_var_to_df(bioclim_df,'CHELSA_bio1_1981-2010_V.2.1.tif')
