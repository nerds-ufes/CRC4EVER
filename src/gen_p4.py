 ################################################################################
 # Copyright 2024 INTRIG
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 ################################################################################

def generate_p4(rec_port, port_user, name_sw, hosts, links,
				routing_model, route_ids, dec_s, route_seq, edge_hosts, crc,
				slice_list, slice_metric):
	
	if (routing_model == 0):
		model = "default"
	if (routing_model == 1):
		model = "polka"

	default_slice = 0
	for i in range(len(slice_list)):
		if slice_list[i][1] == 0: 
			default_slice = 1

	f = open("./files/p7_" + model + ".p4", "w")


	# License
	f.write("/*******************************************************************************\n")
	f.write(" * Copyright 2024 INTRIG\n")
	f.write(" *\n")
	f.write(" * Licensed under the Apache License, Version 2.0 (the \"License\");\n")
	f.write(" * you may not use this file except in compliance with the License.\n")
	f.write(" * You may obtain a copy of the License at\n")
	f.write(" *\n")
	f.write(" *     http://www.apache.org/licenses/LICENSE-2.0\n")
	f.write(" *\n")
	f.write(" * Unless required by applicable law or agreed to in writing, software\n")
	f.write(" * distributed under the License is distributed on an \"AS IS\" BASIS,\n")
	f.write(" * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n")
	f.write(" * See the License for the specific language governing permissions and\n")
	f.write(" * limitations under the License.\n")
	f.write(" ******************************************************************************/\n")
	f.write("\n")
	
	# Libraries
	f.write("#include <tna.p4>\n")
	f.write("\n")
	f.write("#include \"common/headers.p4\"\n")
	f.write("#include \"common/util.p4\"\n")
	f.write("\n")
	f.write("\n")

	# Constants and types
	f.write("/*************************************************************************\n")
	f.write(" ************* C O N S T A N T S    A N D   T Y P E S  *******************\n")
	f.write("**************************************************************************/\n")
	if (len(hosts) > 0):
		f.write("const vlan_id_t p7_vlan = " + str(hosts[0][6]) + ";        // vlan for P7\n")
		f.write("const bit<16> total_sw = " + str(len(name_sw)) + ";         // total number of switches\n")
		for i in range(len(links)):
			f.write("const bit<10> pkt_loss" + str(i) + " = " + str(hex(int(round(10.2*links[i][3])))) + ";       // packet loss  - " + str(links[i][3]) + "%\n")
		f.write("const PortId_t rec_port = " + str(rec_port) + ";       // recirculation port\n")
		f.write("const PortId_t port_user = " + str(port_user) + ";       // recirculation port\n")
		for i in range(len(links)):
			f.write("const bit<32> latency" + str(i) + " = " + str(links[i][4]*1000000) + ";   // latency" + str(i) + "  - " + str(links[i][4]*1000000) + " - " + str(links[i][4]) + "ms\n")
		f.write("const bit<32> constJitter = " + str(links[0][5]*1000000) + ";   // jitter  - " + str(links[0][5]*1000000) + " - " + str(links[0][5]) + "ms\n")
		f.write("const bit<7> percentTax = " + str(int(links[0][6]*127/100)) + ";   // percent*127/100\n")
	else:
		f.write("const vlan_id_t p7_vlan = 9999;        // vlan for P7\n")
		f.write("const bit<16> total_sw = 0;         // total number of switches\n")
		for i in range(len(links)):
			f.write("const bit<10> pkt_loss" + str(i) + " = 0;       // packet loss  - " + str(links[i][3]) + "%\n")
		f.write("const PortId_t rec_port = 68;       // recirculation port\n")
		for i in range(len(links)):
			f.write("const bit<32> latency" + str(i) + " = 0;   // latency" + str(i) + "  - 10000000 - 10ms\n")
		f.write("const bit<32> constJitter = 0\n")
		f.write("const bit<7> percentTax = 0\n")
	f.write("\n")
	
	# Ingress start
	f.write("/*************************************************************************\n")
	f.write("**************  I N G R E S S   P R O C E S S I N G   *******************\n")
	f.write("*************************************************************************/\n")
	f.write("\n")

	# Headers initialization
	# Headers structure is defined in common/headers.p4
	f.write("/***********************  H E A D E R S  ************************/\n")
	f.write("\n")
	f.write("struct my_ingress_metadata_t {\n")
	f.write("    bit<32>  ts_diff;\n")
	f.write("    bit<32>  jitter_metadata;\n")
	f.write("    bit<1>   signal_metadata;\n")
	f.write("    bit<31>  padding;\n")
	f.write("\n")
	if (routing_model == 1):
		f.write("    // PolKa\n")
		if (crc == 8):
			f.write("    bit<152> ndata;\n")
			f.write("    bit<8> diff;\n")
			f.write("    bit<8> nres;\n")
		if (crc == 16):
			f.write("    bit<144> ndata;\n")
			f.write("    bit<16> diff;\n")
			f.write("    bit<16> nres;\n")

	f.write("}\n")
	f.write("\n")

	# Metadata
	f.write("    /******  G L O B A L   I N G R E S S   M E T A D A T A  *********/\n")
	f.write("\n")

	# Ingress Parser
	f.write("parser SwitchIngressParser(\n")
	f.write("       packet_in packet, \n")
	f.write("       out headers hdr, \n")
	f.write("       out my_ingress_metadata_t md,\n")
	f.write("       out ingress_intrinsic_metadata_t ig_intr_md) {\n")
	f.write("\n")
	f.write("    state start {\n")
	f.write("        packet.extract(ig_intr_md);\n")
	f.write("        packet.advance(PORT_METADATA_SIZE);\n")
	f.write("        transition parse_ethernet;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    state parse_ethernet {\n")
	f.write("        packet.extract(hdr.ethernet);\n")
	f.write("        transition select(hdr.ethernet.ether_type) {\n")
	f.write("            ETHERTYPE_ARP:  parse_arp;\n")
	f.write("            ETHERTYPE_IPV4:  parse_ipv4;\n")
	f.write("            ETHERTYPE_VLAN:  parse_vlan;\n")
	f.write("            ETHERTYPE_REC:   parse_rec;   // Recirculation header\n")
	f.write("            default: accept;\n")
	f.write("        }\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    state parse_vlan {\n")
	f.write("        packet.extract(hdr.vlan_tag);\n")
	f.write("        transition select(hdr.vlan_tag.ether_type) {\n")
	f.write("            ETHERTYPE_ARP:  parse_arp;\n")
	f.write("            ETHERTYPE_IPV4:  parse_ipv4;\n")
	f.write("            default: accept;\n")
	f.write("        }\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    state parse_arp {\n")
	f.write("        packet.extract(hdr.arp);\n")
	f.write("        transition accept;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    state parse_ipv4 {\n")
	f.write("        packet.extract(hdr.ipv4);\n")
	if (routing_model == 0):
		f.write("        transition accept;\n")
	if (routing_model == 1):
		f.write("        transition select(hdr.ipv4.protocol) {\n")
		f.write("            IP_PROTOCOLS_TCP: parse_tcp;\n")
		f.write("            IP_PROTOCOLS_UDP: parse_udp;\n")
		f.write("            default: accept;\n")
		f.write("        }\n")
	f.write("    }\n")
	f.write("\n")
	if (routing_model == 1):
		f.write("    state parse_tcp {\n")
		f.write("        packet.extract(hdr.tcp);\n")
		f.write("        transition accept;\n")
		f.write("    }\n")
		f.write("\n")
		f.write("    state parse_udp {\n")
		f.write("        packet.extract(hdr.udp);\n")
		f.write("        transition accept;\n")
		f.write("    }\n")
		f.write("\n")
	f.write("    state parse_rec {\n")
	f.write("        packet.extract(hdr.rec);\n")
	f.write("        transition parse_vlan;\n")
	f.write("    }\n")
	f.write("}\n")
	f.write("\n")

	# Ingress deparser
	f.write("control SwitchIngressDeparser(\n")
	f.write("        packet_out pkt,\n")
	f.write("        inout headers hdr,\n")
	f.write("        in my_ingress_metadata_t ig_md,\n")
	f.write("        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {\n")
	f.write("\n")
	f.write("    apply {\n")
	f.write("        pkt.emit(hdr);\n")
	f.write("    }\n")
	f.write("}\n")
	f.write("\n")

	# Ingress  
	f.write("control SwitchIngress(\n")
	f.write("        inout headers hdr, \n")
	f.write("        inout my_ingress_metadata_t md,\n")
	f.write("        in ingress_intrinsic_metadata_t ig_intr_md,\n")
	f.write("        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,\n")
	f.write("        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md,\n")
	f.write("        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {\n")
	f.write("\n")

	#PolKa CRC definition
	if (routing_model == 1):
		f.write("    // PolKa routing\n")
		for i in name_sw:
			if not (i == edge_hosts[0][1] or i == edge_hosts[1][1]):
				f.write("    CRCPolynomial<bit<" + str(crc) + ">>(\n")
				if (crc == 8):
					f.write("                            coeff    = (" + str(dec_s[int(i[2:]) - 1]) + " & 0xff),\n")
				elif (crc == 16):
					f.write("                            coeff    = (" + str(dec_s[int(i[2:]) - 1]) + " & 0xffff),\n")
				f.write("                            reversed = false,\n")
				f.write("                            msb      = false,\n")
				f.write("                            extended = false,\n")
				if (crc == 8):
					f.write("                            init     = 8w0x00,\n")
					f.write("                            xor      = 8w0x00) poly" + str(int(i[2:])) + ";\n")
				elif (crc == 16):
					f.write("                            init     = 16w0x0000,\n")
					f.write("                            xor      = 16w0x0000) poly" + str(int(i[2:])) + ";\n")
				f.write("    Hash<bit<" + str(crc) + ">>(HashAlgorithm_t.CUSTOM, poly" + str(int(i[2:])) + ") hash" + str(int(i[2:])) + ";\n")
				f.write("\n")

	# Random value for pkt loss and jitter
	f.write("    // Random value used to calculate pkt loss jitter\n")
	f.write("    Random<bit<10>>() rnd;\n")
	f.write("    Random<bit<7>>() percent;\n")
	f.write("    Random<bit<1>>() signalSelector;\n")
	f.write("\n")

	# Register for latency timer
	f.write("    // Register to validate the latency value\n")
	for i in range(len(links)):
		f.write("    Register <bit<32>, _> (32w1)  tscal" + str(i) + ";\n")
	f.write("    Register <bit<32>, _> (32w1)  ax;\n")
	f.write("\n")
	for i in range(len(links)):
		f.write("    RegisterAction<bit<32>, bit<1>, bit<8>>(tscal" + str(i) + ") tscal_action" + str(i) + " = {\n")
		f.write("        void apply(inout bit<32> value, out bit<8> readvalue){\n")
		f.write("            value = 0;\n")
		f.write("            if (md.ts_diff > latency" + str(i) + "){ // @1-latency\n")
		f.write("                readvalue = 1;\n")
		f.write("            }else {\n")
		f.write("                readvalue = 0;\n")
		f.write("            }\n")
		f.write("        }\n")
		f.write("    };\n")
		f.write("\n")

	# Register for jitter
	f.write("    RegisterAction<bit<32>, bit<1>, bit<8>>(ax) ax_action = {\n")
	f.write("        void apply(inout bit<32> value, out bit<8> readvalue){\n")
	f.write("            value = 0;\n")
	f.write("            if (md.ts_diff > constJitter){ // @jitter\n")
	f.write("                readvalue = 1;\n")
	f.write("            }else {\n")
	f.write("                readvalue = 0;\n")
	f.write("            }\n")
	f.write("        }\n")
	f.write("    };\n")
	f.write("\n")

	# Actions
	f.write("    action drop() {\n")
	f.write("        ig_intr_dprsr_md.drop_ctl = 0x1;\n")
	f.write("    }\n")
	f.write("\n")
	if (routing_model == 1):
		f.write("    action NoAction(){}\n")
		f.write("\n")
	f.write("    // Send the packet to output port\n")
	f.write("    // Remove the recirculation header\n")
	f.write("    // Set back the ethertype of the original packet\n")
	f.write("    action send(PortId_t port) {\n")
	f.write("        //hdr.ethernet.src_addr[31:0] = hdr.rec.num;\n")
	f.write("        hdr.ethernet.ether_type = hdr.rec.ether_type;\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = port;\n")
	f.write("        hdr.rec.setInvalid();\n")
	f.write("        ig_intr_tm_md.bypass_egress = 1w1;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // Send packet to the next internal switch \n")
	f.write("    // Reset the initial timestamp\n")
	f.write("    // Increase the ID of the switch\n")
	if (routing_model == 0):
		f.write("    action send_next(bit<16> link_id, bit<16> sw_id) {\n")
	if (routing_model == 1):
		f.write("    action send_next(bit<16> sw_id) {\n")
		f.write("        // PolKa routing\n")
		if (crc == 8):
			f.write("        md.ndata = (bit<152>) (hdr.rec.routeid >> 8);\n")
			f.write("        md.diff = (bit<8>) hdr.rec.routeid;\n")
		if (crc == 16):
			f.write("        md.ndata = (bit<144>) (hdr.rec.routeid >> 16);\n")
			f.write("        md.diff = (bit<16>) hdr.rec.routeid;\n")
		f.write("\n")
	f.write("        hdr.rec.ts = ig_intr_md.ingress_mac_tstamp[31:0];\n")
	f.write("        hdr.rec.num = 1;\n")
	f.write("\n")
	if (routing_model == 0):
		f.write("        hdr.rec.sw = link_id;\n")
	f.write("        hdr.rec.sw_id = sw_id;\n")
	f.write("\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = port_user;\n")
	f.write("    }\n")
	f.write("\n")

	if (routing_model == 1):
		for i in name_sw:
			if (i == edge_hosts[0][1] or i == edge_hosts[1][1]):
				f.write("    action send_next_" + str(int(i[2:])) + "(bit<16> link_id) {\n")
				f.write("        hdr.rec.sw = link_id;\n")
				f.write("    }\n")
			else:
				f.write("    action send_next_" + str(int(i[2:])) + "() {\n")
				f.write("        // PolKa routing\n")
				f.write("        md.nres = hash" + str(int(i[2:])) + ".get(md.ndata);\n")
				f.write("        hdr.rec.sw = (bit<16>) (md.nres^md.diff); // Next link by PolKa\n")
				f.write("    }\n")

	f.write("    // Forward a packet directly without any P7 processing\n")
	f.write("    action send_direct(PortId_t port) {\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = port;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // Recirculate the packet to the recirculation port\n")
	f.write("    // Increase the recirculation number\n")
	f.write("    action recirculate(PortId_t recirc_port){\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = recirc_port;\n")
	f.write("        hdr.rec.num = hdr.rec.num + 1;      // using new header\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // Calculate the difference between the initial timestamp a the current timestamp\n")
	f.write("    action comp_diff() {\n")
	f.write("         md.ts_diff = ig_intr_md.ingress_mac_tstamp[31:0] - hdr.rec.ts;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // increases jitter in the timestamp difference\n")
	f.write("    action apply_more_jitter(){\n")
	f.write("	  md.ts_diff = md.ts_diff + hdr.rec.jitter;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // decreases jitter in the timestamp difference\n")
	f.write("    action apply_less_jitter(){\n")
	f.write("    	  md.ts_diff = md.ts_diff - hdr.rec.jitter;\n")
	f.write("    }\n")
	f.write("\n")
	f.write("    // Match incoming packet\n")
	f.write("    // Add recirculation header\n")
	f.write("    // Save the ethertype of the original packet in the recirculation header - ether_type\n")
	f.write("    // Save the initial timestamp (ingress_mac_tstamp) in the recirculation header - ts\n")
	f.write("    // Set the starting number of recirculation - num\n")
	f.write("    // Set the ID of the first switch - sw\n")
	if (routing_model == 0 or (routing_model == 1 and default_slice == 0)):
		f.write("    action match(bit<16> link) {\n")
	if (routing_model == 1 and default_slice == 1):
		f.write("    action match(bit<16> link, bit<160> routeIdPacket) {\n")
	f.write("        hdr.rec.setValid();\n")
	f.write("        hdr.rec.ts = ig_intr_md.ingress_mac_tstamp[31:0];\n")
	f.write("        hdr.rec.num = 1;\n")
	f.write("        hdr.rec.sw = link;\n")
	f.write("        hdr.rec.dest_ip = hdr.ipv4.dst_addr;\n")
	f.write("        hdr.rec.ether_type = hdr.ethernet.ether_type;\n")
	f.write("        hdr.vlan_tag.vid = p7_vlan;\n")
	f.write("\n")
	f.write("        hdr.rec.jitter = md.jitter_metadata;\n")
	f.write("        hdr.rec.signal = md.signal_metadata;\n")
	f.write("\n")
	f.write("        hdr.ethernet.ether_type = 0x9966;\n")
	f.write("\n")
	if (routing_model == 1 and default_slice == 1):
		f.write("        hdr.rec.routeid = routeIdPacket;\n")
		f.write("\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = rec_port;\n")
	f.write("        ig_intr_tm_md.bypass_egress = 1w1;\n")
	f.write("    }\n")

	f.write("\n")
	if (routing_model == 0):
		f.write("    action match_arp(bit<16> link) {\n")
	if (routing_model == 1):
		f.write("    action match_arp(bit<16> link, bit<160> routeIdPacket) {\n")
	f.write("        hdr.rec.setValid();\n")
	f.write("        hdr.rec.ts = ig_intr_md.ingress_mac_tstamp[31:0];\n")
	f.write("        hdr.rec.num = 1;\n")
	f.write("        hdr.rec.sw = link;\n")
	f.write("        hdr.rec.dest_ip = hdr.arp.dest_ip;\n")
	f.write("        hdr.rec.ether_type = hdr.ethernet.ether_type;\n")
	f.write("        hdr.vlan_tag.vid = p7_vlan;\n")
	f.write("\n")
	f.write("        hdr.rec.jitter = md.jitter_metadata;\n")
	f.write("        hdr.rec.signal = md.signal_metadata;\n")
	f.write("\n")
	f.write("        hdr.ethernet.ether_type = 0x9966;\n")
	f.write("\n")
	if (routing_model == 1):
		f.write("        hdr.rec.routeid = routeIdPacket;\n")
		f.write("\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = rec_port;\n")
	f.write("        ig_intr_tm_md.bypass_egress = 1w1;\n")
	f.write("    }\n")

	f.write("\n")
	f.write("    action match_arp_direct(PortId_t port) {\n")
	f.write("        ig_intr_tm_md.ucast_egress_port = port;\n")
	f.write("    }\n")
	f.write("\n")
	if (routing_model == 1):
		f.write("    // Slice\n")
		f.write("    action slice_select_dst(bit<160> routeIdPacket){\n")
		f.write("        hdr.rec.routeid = routeIdPacket;\n")
		f.write("    }\n")
		f.write("\n")
		f.write("    action slice_select_src(bit<160> routeIdPacket){\n")
		f.write("        hdr.rec.routeid = routeIdPacket;\n")
		f.write("    }\n")
		f.write("\n")
	f.write("    // Table perform l2 forward\n")
	f.write("    // Match the interconnection ID and the destination IP\n")
	f.write("    table basic_fwd {\n")
	f.write("        key = {\n")
	f.write("            hdr.rec.sw : exact;\n")
	f.write("            hdr.rec.dest_ip   : exact;\n")
	f.write("        }\n")
	f.write("        actions = {\n")
	f.write("            send_next;\n")
	f.write("            send;\n")
	f.write("            @defaultonly drop;\n")
	f.write("        }\n")
	f.write("        const default_action = drop();\n")
	f.write("        size = 128;\n")
	f.write("    }\n")
	f.write("\n")

	if (routing_model == 1):
		f.write("    table basic_fwd_hash {\n")
		f.write("        key = {\n")
		f.write("            hdr.rec.sw_id : exact;\n")
		f.write("            hdr.rec.dest_ip   : exact;\n")
		f.write("        }\n")
		f.write("        actions = {\n")
		for i in name_sw:
			f.write("            send_next_" + str(int(i[2:])) + ";\n")
		f.write("            @defaultonly drop;\n")
		f.write("        }\n")
		f.write("        const default_action = drop();\n")
		f.write("        size = 128;\n")
		f.write("    }\n")

	f.write("\n")
	f.write("    // Table to verify the VLAN_ID to be processed by P7\n")
	f.write("    // Match the VLAN_ID and the ingress port\n")
	f.write("    table vlan_fwd {\n")
	f.write("        key = {\n")
	f.write("            hdr.vlan_tag.vid   : exact;\n")
	f.write("            ig_intr_md.ingress_port : exact;\n")
	f.write("        }\n")
	f.write("        actions = {\n")
	f.write("            send_direct;\n")
	f.write("            match;\n")
	f.write("            @defaultonly drop;\n")
	f.write("        }\n")
	f.write("        const default_action = drop();\n")
	f.write("        size = 128;\n")
	f.write("    }\n")


	f.write("\n")
	f.write("    table arp_fwd {\n")
	f.write("        key = {\n")
	f.write("            hdr.vlan_tag.vid   : exact;\n")
	f.write("            ig_intr_md.ingress_port : exact;\n")
	f.write("        }\n")
	f.write("        actions = {\n")
	f.write("            match_arp;\n")
	f.write("            match_arp_direct;\n")
	f.write("            @defaultonly drop;\n")
	f.write("        }\n")
	f.write("        const default_action = drop();\n")
	f.write("        size = 128;\n")
	f.write("    }\n")
	f.write("\n")

	if (routing_model == 1):
		f.write("   table slice_dst {\n")
		f.write("       key = {\n")
		if slice_metric == "TCP":
			f.write("           hdr.tcp.dst_port   : exact;\n")
		elif slice_metric == "UDP":
			f.write("           hdr.udp.dst_port   : exact;\n")
		elif slice_metric == "ToS":
			f.write("           hdr.ipv4.diffserv   : exact;\n")
			f.write("           hdr.rec.dest_ip   	: exact;\n")
		f.write("       }\n")
		f.write("       actions = {\n")
		f.write("           slice_select_dst;\n")
		f.write("           @defaultonly NoAction;\n")
		f.write("       }\n")
		f.write("       const default_action = NoAction();\n")
		f.write("       size = 128;\n")
		f.write("   }\n")
		f.write("\n")
		if slice_metric == "TCP" or slice_metric == "UDP":
			f.write("   table slice_src {\n")
			f.write("       key = {\n")
			if slice_metric == "TCP":
				f.write("           hdr.tcp.src_port   : exact;\n")
			elif slice_metric == "UDP":
				f.write("           hdr.udp.src_port   : exact;\n")
			f.write("       }\n")
			f.write("       actions = {\n")
			f.write("           slice_select_src;\n")
			f.write("           @defaultonly NoAction;\n")
			f.write("       }\n")
			f.write("       const default_action = NoAction();\n")
			f.write("       size = 128;\n")
			f.write("   }\n")

	f.write("\n")
	f.write("    apply {\n")
	f.write("        //sets the jitter to be applied\n")
	f.write("	 if(!hdr.rec.isValid()){\n")
	f.write("	     bit<7> P = percent.get();\n")
	f.write("	     if(P <= percentTax){\n")
	f.write("	         md.jitter_metadata = constJitter;\n")
	f.write("		 md.signal_metadata = signalSelector.get();\n")
	f.write("	     }\n")
	f.write("	     else{\n")
	f.write("		 md.jitter_metadata = 0;\n")
	f.write("		 md.signal_metadata = 0;\n")
	f.write("	     }\n")
	f.write("	  }\n")

	f.write("        // Validate if the incoming packet has VLAN header\n")
	f.write("        // Match the VLAN_ID with P7\n")
	f.write("        if (hdr.vlan_tag.isValid() && !hdr.rec.isValid() && !hdr.arp.isValid()) {\n")
	f.write("            vlan_fwd.apply();\n")
	if (routing_model == 1):
		if slice_metric == "ToS":
			f.write("            slice_dst.apply();\n")
		else:
			f.write("            slice_dst.apply();\n")
			f.write("            slice_src.apply();\n")
	f.write("        }\n")
	f.write("        else if (hdr.vlan_tag.isValid() && !hdr.rec.isValid() && hdr.arp.isValid()) {\n")
	f.write("            arp_fwd.apply();\n")
	f.write("        } else {\n")
	f.write("            // If the recirculation header is valid, match the switch ID\n")
	f.write("            // Then verify the timestamp difference (latency)\n")
	f.write("            // Apply the packet_loss value with the random number generated\n")
	f.write("            // Verify if the switch is the final one or need to be processed by the next one\n")
	f.write("            if (hdr.rec.isValid()) {\n")
	f.write("                //Number of switch\n")
	for i in range(len(links)):
		if i == 0:
			f.write("                if (hdr.rec.sw == " + str(i) + "){                   // " + str(i) + " - ID switch\n")
		else:
			f.write("                else if (hdr.rec.sw == " + str(i) + "){                   // " + str(i) + " - ID switch\n")
		f.write("                    bit<8> value_tscal;\n")
		f.write("                    md.ts_diff = 0;\n")
		f.write("                    comp_diff();\n")
		f.write("    		     //apply the jitter\n")
		f.write("		     if(hdr.rec.signal==0){\n")
		f.write("		         apply_more_jitter();\n")
		f.write("      		     }else{\n")
		f.write("   		         if(ax_action.execute(1)==1)\n")
		f.write("		     	     apply_less_jitter();\n")
		f.write("		     }\n")
		f.write("                    value_tscal = tscal_action" + str(i) + ".execute(1);\n")
		f.write("                    if (value_tscal == 1){\n")
		f.write("                        bit<10> R = rnd.get();\n")
		f.write("                        if (R >= pkt_loss" + str(i) + ") {            // @2-% of pkt loss \n")
		f.write("                            basic_fwd.apply();\n")
		if (routing_model == 1):
			f.write("                            basic_fwd_hash.apply();\n")
		f.write("                        }else{\n")
		f.write("                            drop();\n")
		f.write("                        } \n")
		f.write("                    }else {\n")
		f.write("                        recirculate(rec_port);          // Recirculation port (e.g., loopback interface)\n")
		f.write("                    }   \n")
		if len(links) > 0 and i < len(links)-1:
			f.write("                }\n")
	f.write("                }else{\n")
	f.write("                    drop();\n")
	f.write("                } \n")
	f.write("            // If the recirculation header is not valid\n")
	f.write("            // Perform the match action to add recirculation header           \n")
	f.write("            }else{\n")
	f.write("               drop();    \n")
	f.write("            }\n")
	f.write("        }\n")
	f.write("\n")
	f.write("        // No need for egress processing, skip it and use empty controls for egress.\n")
	f.write("        ig_intr_tm_md.bypass_egress = 1w1;\n")
	f.write("    }\n")
	f.write("}\n")
	f.write("\n")

	# Pipeline
	f.write("Pipeline(SwitchIngressParser(),\n")
	f.write("         SwitchIngress(),\n")
	f.write("         SwitchIngressDeparser(),\n")
	f.write("         EmptyEgressParser(),\n")
	f.write("         EmptyEgress(),\n")
	f.write("         EmptyEgressDeparser()) pipe_p7;\n")
	f.write("\n")
	f.write("Switch(pipe_p7) main;\n")


	f.close()
