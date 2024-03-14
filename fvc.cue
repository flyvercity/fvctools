timestamp: {
	unix: float
}

ids: {
	fvc_uas_id: string
	caa_uas_id: string
}

location: {
	lat:  float
	lon:  float
	alt:  float
	baro: float
}

attitide: {
	roll:    float
	pitch:   float
	yaw:     float
	heading: float
}

speeds: {
	vnorth: float
	vdown:  float
	vair:   float
}

position: {
	location: location
	attitide: attitide
	speeds:   speeds
}

signal: {
	radio:   string
	RSRP:    integer
	RSRQ:    integer
	RSRP_4G: integer
	RSRQ_4G: integer
	RSRP_5G: integer
	RSRQ_5G: integer
	cell:    string
	band:    string
}

performance: {
	heartbeat_loss: boolean
	RTT:            float
}

packet: {
	ids:       ids
	timestamp: timestamp
	position:  position
	signal:    signal
}
