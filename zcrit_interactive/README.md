# Create an interactive plot of Zcrit using Plotly + Dash

Link to [Plotly](https://plotly.com/python/)
Link to [Dash](https://dash.plotly.com/)
Link to [Lim et al. (2024)](https://arxiv.org/abs/2312.12508)

'collapse_data.txt' contains whether a simulation forms planetesimals (Y) or not (N). First three columns show alpha, tau, and Z values of each run. 

'.csv file' contains maximum particle density (dmax), scale height of particles (hp), and mid-plane particle-to-gas density ratio (eps) as a function of time (time). These files are named by the simulations' initial conditions. The numbers after tau and Z are these values, and 1,2, or 3 in the third segmant of each filename corresponds to alpha values; 1 for alpha=1.e-4, 2 for 3.3e-4,3 for 1.e-3. The four digits numbers after sg refer to the simulation time in unit of '1/\Omega' at which particle self-gravity is switched on. 

'assets' directory contains final snapshots of particle density distribution in each simulation. 

'app.py' is a python script that is used to plot the interactive figure.

Note that by default, Dash apps run on 'localhost'—you can only access them on your own machine. To share a Dash app, you need to deploy it to a server

The interative plot here is deployed to Google Cloud to get a public URL to this plot. 

To learn how to deploy using Google Cloud, the best resource I've found is this [YouTube](https://www.youtube.com/watch?v=1VewIO2Yhmo&t=216s) by 
Federico Tartarini


##command for deployment into Google Cloud (The gcloud CLI must be installed)  

gcloud builds submit --tag gcr.io/turb-si-interactive-zcrit/turb-si-interactive-zcrit-plot  --project=turb-si-interactive-zcrit

gcloud run deploy --image gcr.io/turb-si-interactive-zcrit/turb-si-interactive-zcrit-plot --platform managed  --project=turb-si-interactive-zcrit --allow-unauthenticated
