//Training GraphSage for Venue Nodes
CALL gds.beta.graphSage.train(
	"venue_projection",
	{
		modelName:"venue_model",
		featureProperties:["n_citation","reference_count"],
		projectedFeatureDimension:2
	}
)