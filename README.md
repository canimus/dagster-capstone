# dagster-capstone
A sample project that uses the foundation concepts for dagster orchestration

# Timeline


## project structure
Create the folders as per the recommended dagster tutorials

- `mkdir -p capstone/{assets,resources,schedules,sensors,partitions}`

## module files
Place files in each module under the capstone project to set up all dagster entities.

- `for i in $(ls -1 capstone);do touch "capstone/$i/__init__.py"; done`
