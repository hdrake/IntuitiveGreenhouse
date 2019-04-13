# IntuitiveGreenhouseEffect

The script `dense_Ts_and_CO2.py` runs the PyRADS radiation code (https://github.com/ddbkoll/PyRADS) for several values of the CO2 concentration and surface temperature and saves the resulting spectra to `output/olr_dense.npz` for temporary storage.

The notebook `plot_olr_movies.ipynb` loads in the spectra in `output/olr_dense.npz` and linearly interpolates between iterations to find the spectrum whose outgoing longwave radiation (OLR) balances with the prescribed absorbed solar radiation, as CO2 concentrations as slowly increased.

