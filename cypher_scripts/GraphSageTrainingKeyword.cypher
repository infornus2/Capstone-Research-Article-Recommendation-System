//Training GraphSage for Keyword Nodes
CALL gds.beta.graphSage.train(
	"keyword_projection",
	{
		modelName:"keyword_model",
		featureProperties:["n_citation","reference_count"],
		projectedFeatureDimension:2
	}
)