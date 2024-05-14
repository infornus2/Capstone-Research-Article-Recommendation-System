//Leiden Algorithm for Community Detection
CALL gds.beta.leiden.write(
  'comm_detect',
  {
    writeProperty:'community'
  }
)
YIELD communityCount, modularity;