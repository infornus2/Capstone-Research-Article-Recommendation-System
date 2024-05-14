//Louvain Algorithm for Community Detection
CALL gds.louvain.write('comm_detect', {
  writeProperty: 'community',
  minCommunitySize:10,
  maxIterations: 1000,
  tolerance: 0.001
})
YIELD communityCount, modularity;