## gamestv.org demo parse and cut service
hosted at https://fr.gtv.msh100.uk/demoparse - big thanks to [Msh100](https://github.com/msh100)
## available methods:
- GET /parse/demo_id - list maps
- GET /parse/demo_id/map_number
  - compressed: `curl --compressed http://localhost:5222/parse/12/1`
## TODO:
- passing parser parameters like export paths
- POST /cut/demo_id/map_number
- run sqlite server of indexed demos
- watch for new demos and parse/index them

## related repos: 
- https://github.com/mittermichal/advanced-gamestv-stats
- https://github.com/mittermichal/Anders.Gaming.LibTech3