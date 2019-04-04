{	
	"BEGIN": {
		"sent": 
			"One [location.time] <br> <b>[subject.name]</b> walked into the <b>[location.name]</b>",
		"edge": {
			"subject.latent.true": {"SWELL": 0.5, "TOLD": 0.5},
			"subject.latent.false": {"SWELL": 0.5, "TOLD": 0.5}
		}
	},

	"SWELL": {
		"sent": 
			"<b>[subject.name]</b> <b>knew!</b> the '[drink.name]'<br> was quite swell here.",
		"edge":{
			"subject.latent.true": {"AFTER": 0.9, "SAW": 0.1},
			"subject.latent.false": {"AFTER": 0.1, "SAW": 0.9}
		}
	},
	"TOLD": {
		"sent": 
			"<b>[subject.name]</b> was <b>told</b> they had<br>[basement.name] in the basement.",
		"edge": {
			"subject.latent.true": {"AFTER": 0.1, "SAW": 0.9},
			"subject.latent.false": {"AFTER": 0.9, "SAW": 0.1}
		}
	},

	"AFTER": {
		"sent": 
			"After ordering, <b>[subject.name]</b> <b>realized</b> <br>'[realize.this]'",
		"edge": {
			"subject.latent.true": {"RADIO": 0.9, "TELE": 0.1},
			"subject.latent.false": {"RADIO": 0.1, "TELE": 0.9}
		}
	},
	"SAW": {
		"sent": 
			"Before ordering, <b>[subject.name]</b> <b>saw</b> <br> '[see.this]'",
		"edge": {
			"subject.latent.true": {"RADIO": 0.1, "TELE": 0.9},
			"subject.latent.false": {"RADIO": 0.9, "TELE": 0.1}
		}
	},

	"RADIO": {
		"sent": 
			"Suddenly, the <b>radio</b> began <br>'[broadcast.this]'",
		"edge": {
			"subject.latent.true": {"RECALL": 0.9, "MEMORY": 0.1},
			"subject.latent.false": {"RECALL": 0.1, "MEMORY": 0.9}
		}
	},
	"TELE": {
		"sent": 
			"<b>Eventually</b> it happened, <br> [eventuality.this]",
		"edge": {
			"subject.latent.true": {"RECALL": 0.1, "MEMORY": 0.9},
			"subject.latent.false": {"RECALL": 0.9, "MEMORY": 0.1}
		}
	},

	"RECALL": {
		"sent": 
			"and <b>[subject.name]</b> recalled <b>[subject.pospronoun] self</b><br>saying in a low voice:",
		"edge": {
			"subject.latent.true": {"STORY": 0.9, "NARRATIVE": 0.1},
			"subject.latent.false": {"STORY": 0.1, "NARRATIVE": 0.9}
		}
	},
	"MEMORY": {
		"sent": 
			"which brought memories of <b>[subject.name]</b>'s <br><b>shaman-guru</b> yelling:",
		"edge": {
			"subject.latent.true": {"STORY": 0.1, "NARRATIVE": 0.9},
			"subject.latent.false": {"STORY": 0.9, "NARRATIVE": 0.1}
		}
	},

	"STORY": {
		"sent": 
			"'Our <b>self-personal-metastory</b> <br>is [saying1.this]'",
		"edge": {
			"subject.latent.true": {"TRANSPORT": 0.9, "TRANSCEND": 0.1},
			"subject.latent.false": {"TRANSPORT": 0.1, "TRANSCEND": 0.9}
		}
	},
	"NARRATIVE": {
		"sent": 
			"'Our <b>introspective-dream-narrative</b> <br>couldn't be [saying2.this]'",
		"edge": {
			"subject.latent.true": {"TRANSPORT": 0.1, "TRANSCEND": 0.9},
			"subject.latent.false": {"TRANSPORT": 0.9, "TRANSCEND": 0.1}
		}
	},

	"TRANSCEND": {
		"sent": 
			"That must have been <br>when <b>[subject.name]</b> <b>transcended</b>.",
		"edge": {
			"subject.latent.true": {"END": 1.0},
			"subject.latent.false": {"END": 1.0}
		}
	},
	"TRANSPORT": {
		"sent": 
			"That was when they saw <br><b>[subject.name]</b> <b>evaporate</b>. <br>",
		"edge": {
			"subject.latent.true": {"END": 1.0},
			"subject.latent.false": {"END": 1.0}
		}
	},

	"END": {
		"sent": 
			"~ FIN ~",
		"edge": {}
	}
}