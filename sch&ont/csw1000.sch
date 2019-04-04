{	
	"BEGIN": {
		"sent": 
			"One [location.time] [subject.name] walked into the [location.name]",
		"edge": {
			"subject.latent.true": {"TERRIBLE": 0.5, "TOLD": 0.5},
			"subject.latent.false": {"TERRIBLE": 0.5, "TOLD": 0.5}
		}
	},

	"TERRIBLE": {
		"sent": 
			"[subject.name] knew the [drink.name] was terrible here",
		"edge":{
			"subject.latent.true": {"NOTICE": 1.0, "HEARD": 0.0},
			"subject.latent.false": {"NOTICE": 0.0, "HEARD": 1.0}
		}
	},
	"TOLD": {
		"sent": 
			"[subject.name] was told they had [basement.name] in the basement",
		"edge": {
			"subject.latent.true": {"NOTICE": 0.0, "HEARD": 1.0},
			"subject.latent.false": {"NOTICE": 1.0, "HEARD": 0.0}
		}
	},

	"NOTICE": {
		"sent": 
			"After ordering,  [subject.name] noticed [notice.this]",
		"edge": {
			"subject.latent.true": {"RADIO": 1.0, "BAND": 0.0},
			"subject.latent.false": {"RADIO": 0.0, "BAND": 1.0}
		}
	},
	"HEARD": {
		"sent": 
			"While sitting down, [subject.name] overheard [overhear.this]",
		"edge": {
			"subject.latent.true": {"RADIO": 0.0, "BAND": 1.0},
			"subject.latent.false": {"RADIO": 1.0, "BAND": 0.0}
		}
	},

	"RADIO": {
		"sent": 
			"Suddenly, the radio began broadcasting [radio.broadcast]",
		"edge": {
			"subject.latent.true": {"DANCE": 1.0, "REVOLT": 0.0},
			"subject.latent.false": {"DANCE": 0.0, "REVOLT": 1.0}
		}
	},
	"BAND": {
		"sent": 
			"That’s when the band began playing [music.title]",
		"edge": {
			"subject.latent.true": {"DANCE": 0.0, "REVOLT": 1.0},
			"subject.latent.false": {"DANCE": 1.0, "REVOLT": 0.0}
		}
	},

	"DANCE": {
		"sent": 
			"This caused [subject.name] to dance [dance.name]",
		"edge": {
			"subject.latent.true": {"COPS": 1.0, "BARISTA": 0.0},
			"subject.latent.false": {"COPS": 0.0, "BARISTA": 1.0}
		}
	},
	"REVOLT": {
		"sent": 
			"[subject.name] was so revolted [subject.pronoun] [subjdeed.this]",
		"edge": {
			"subject.latent.true": {"COPS": 0.0, "BARISTA": 1.0},
			"subject.latent.false": {"COPS": 1.0, "BARISTA": 0.0}
		}
	},

	"BARISTA": {
		"sent": 
			"The barista had to intervene by [barista.deed] at [subject.name]",
		"edge": {
			"subject.latent.true": {"TAKEOBJ": 0.0, "FOODLEAVE": 1.0},
			"subject.latent.false": {"TAKEOBJ": 1.0, "FOODLEAVE": 0.0}
		}
	},
	"COPS": {
		"sent": 
			"The police came rushing in [cops.deed] [subject.name]",
		"edge": {
			"subject.latent.true": {"TAKEOBJ": 1.0, "FOODLEAVE": 0.0},
			"subject.latent.false": {"TAKEOBJ": 0.0, "FOODLEAVE": 1.0}
		}
	},
	

	"FOODLEAVE": {
		"sent": 
			"[subject.name] just took [subject.pronoun2] [food.name] and left",
		"edge": {
			"subject.latent.true": {"END": 1.0},
			"subject.latent.false": {"END": 1.0}
		}
	},
	"TAKEOBJ": {
		"sent": 
			"On [subject.pronoun2] way out, [subject.name] took the [taken.object]",
		"edge": {
			"subject.latent.true": {"END": 1.0},
			"subject.latent.false": {"END": 1.0}
		}
	},

	"END": {
		"sent": 
			"That is all that is remembered.",
		"edge": {}
	}
}