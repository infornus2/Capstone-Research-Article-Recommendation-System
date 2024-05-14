CALL gds.graph.project(
	"keyword_projection",
	{
		Paper:{
			label:"Paper",
			properties:{
				n_citation:{
					property:"n_citation",
					defaultValue:0
				
				},
				reference_count:{
					property:"reference_count",
					defaultValue:0
				
				},
				year:{
					property:"year"
				
				}
				}
			},
		Keyword:{
			label:"Keyword"
		}
	},
	{
		HAS_KEYWORD:{type:"HAS_KEYWORD",orientation:"UNDIRECTED"}
	}
			
				
)
