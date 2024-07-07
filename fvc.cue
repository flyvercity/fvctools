timestamp: {
	unix: float
}

ua_ids: {
	fvc_uas_id:  string
	caa_uas_id?: string
}

location: {
	lat:   float // Degrees
	lon:   float // Degrees
	alt:   float // Meters
	baro?: float // Meters
}

attitide: {
	roll?:    float // Degrees
	pitch?:   float // Degrees
	yaw?:     float // Degrees
	heading?: float // Degrees from North clockwise
}

speeds: {
	vnorth?: float
	veast?:  float
	vdown?:  float
	vair?:   float
}

position: {
	location:  location
	attitide?: attitide
	speeds?:   speeds
}

signal: {
	radio:    string
	RSRP:     int
	RSRQ:     int
	RSRP_4G?: int
	RSRQ_4G?: int
	RSRP_5G?: int
	RSRQ_5G?: int
	cell?:    string
	band?:    string
}

performance: {
	heartbeat_loss: bool
	RTT:            float
}

#cell_log: {
	ids:       ids
	timestamp: timestamp
	position:  position
	signal:    signal
	...
}
