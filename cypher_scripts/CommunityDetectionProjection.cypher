//Creating Graph Projection for Community Detection
CALL gds.graph.project(
	"comm_detect",
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
		Author:{
			label:"Author"			
		},
		Keyword:{
			label:"Keyword"
		},
		Venue:{
			label:"Venue"
		}
	},
	{
		AUTHORED:{type:"AUTHORED",orientation:"UNDIRECTED"},
		PUBLISHED_IN:{type:"PUBLISHED_IN",orientation:"UNDIRECTED"},
		HAS_KEYWORD:{type:"HAS_KEYWORD",orientation:"UNDIRECTED"}
	}
			
				
)
