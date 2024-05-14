//Label Propagation Algorithm for Community Detection
CALL gds.labelPropagation.write('comm_detect', {
  writeProperty: 'community',
  maxIterations: 50
})
YIELD communityCount
RETURN communityCount;