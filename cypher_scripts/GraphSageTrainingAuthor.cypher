//Training GraphSage for Author Nodes
CALL gds.beta.graphSage.train(
	"author_projection",
	{
		modelName:"author_model",
		featureProperties:["n_citation","reference_count"],
		projectedFeatureDimension:2
	}
)