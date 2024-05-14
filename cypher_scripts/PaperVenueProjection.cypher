CALL gds.graph.project(
	"venue_projection",
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
		Venue:{
			label:"Venue"			
		},
		Keyword:{
			label:"Keyword"
		},
		Venue:{
			label:"Venue"
		}
	},
	{
		PUBLISHED_IN:{type:"PUBLISHED_IN",orientation:"UNDIRECTED"}
	}		
)
