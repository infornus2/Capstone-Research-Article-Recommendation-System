CALL gds.graph.project(
	"author_projection",
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
		}
	},
	{
		AUTHORED:{type:"AUTHORED",orientation:"UNDIRECTED"}
	}
				
)
