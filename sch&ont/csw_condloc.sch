{	
	"BEGIN": {
		"sent": 
			"One [location.time] <br> [subject.name] walked into the <b>[location.name]</b>",
		"edge": {
			"location.latent.true": {"SWELL": 0.5, "TOLD": 0.5},
			"location.latent.false": {"SWELL": 0.5, "TOLD": 0.5}
		}
	},

	"SWELL": {
		"sent": 
			"[subject.name] <b>knew!</b> the '[drink.name]'<br> was quite swell here.",
		"edge":{
			"location.latent.true": {"AFTER": 0.8, "SAW": 0.2},
			"location.latent.false": {"AFTER": 0.2, "SAW": 0.8}
		}
	},
	"TOLD": {
		"sent": 
			"[subject.name] was <b>told</b> they had<br>[basement.name] in the basement.",
		"edge": {
			"location.latent.true": {"AFTER": 0.2, "SAW": 0.8},
			"location.latent.false": {"AFTER": 0.8, "SAW": 0.2}
		}
	},

	"AFTER": {
		"sent": 
			"After ordering, [subject.name] <b>realized</b> <br>'[realize.this]'",
		"edge": {
			"location.latent.true": {"RADIO": 0.8, "TELE": 0.2},
			"location.latent.false": {"RADIO": 0.2, "TELE": 0.8}
		}
	},
	"SAW": {
		"sent": 
			"Before ordering, [subject.name] <b>saw</b> <br> '[see.this]'",
		"edge": {
			"location.latent.true": {"RADIO": 0.2, "TELE": 0.8},
			"location.latent.false": {"RADIO": 0.8, "TELE": 0.2}
		}
	},

	"RADIO": {
		"sent": 
			"Suddenly, the <b>radio</b> began <br>'[broadcast.this]'",
		"edge": {
			"location.latent.true": {"RECALL": 0.8, "MEMORY": 0.2},
			"location.latent.false": {"RECALL": 0.2, "MEMORY": 0.8}
		}
	},
	"TELE": {
		"sent": 
			"<b>Eventually</b> it happened, <br> [eventuality.this]",
		"edge": {
			"location.latent.true": {"RECALL": 0.2, "MEMORY": 0.8},
			"location.latent.false": {"RECALL": 0.8, "MEMORY": 0.2}
		}
	},

	"RECALL": {
		"sent": 
			"and [subject.name] recalled <b>[subject.pospronoun] self</b><br>saying in a low voice:",
		"edge": {
			"location.latent.true": {"STORY": 0.8, "NARRATIVE": 0.2},
			"location.latent.false": {"STORY": 0.2, "NARRATIVE": 0.8}
		}
	},
	"MEMORY": {
		"sent": 
			"which brought memories of [subject.name]'s <br><b>shaman-guru</b> yelling:",
		"edge": {
			"location.latent.true": {"STORY": 0.2, "NARRATIVE": 0.8},
			"location.latent.false": {"STORY": 0.8, "NARRATIVE": 0.2}
		}
	},

	"STORY": {
		"sent": 
			"'Our <b>self-personal-metastory</b> <br>is [saying1.this]'",
		"edge": {
			"location.latent.true": {"TRANSPORT": 0.8, "TRANSCEND": 0.2},
			"location.latent.false": {"TRANSPORT": 0.2, "TRANSCEND": 0.8}
		}
	},
	"NARRATIVE": {
		"sent": 
			"'Our <b>introspective-dream-narrative</b> <br>couldn't be [saying2.this]'",
		"edge": {
			"location.latent.true": {"TRANSPORT": 0.2, "TRANSCEND": 0.8},
			"location.latent.false": {"TRANSPORT": 0.8, "TRANSCEND": 0.2}
		}
	},

	"TRANSCEND": {
		"sent": 
			"That must have been <br>when [subject.name] <b>transcended</b>.",
		"edge": {
			"location.latent.true": {"END": 1.0},
			"location.latent.false": {"END": 1.0}
		}
	},
	"TRANSPORT": {
		"sent": 
			"That was when they saw <br>[subject.name] <b>evaporate</b>. <br>",
		"edge": {
			"location.latent.true": {"END": 1.0},
			"location.latent.false": {"END": 1.0}
		}
	},

	"END": {
		"sent": 
			"~ FIN ~",
		"edge": {}
	}
}