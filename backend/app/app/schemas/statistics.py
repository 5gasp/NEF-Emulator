from threading import Event
from typing import List, Optional
from pydantic import BaseModel, Field, IPvAnyAddress, AnyHttpUrl, constr
from enum import Enum


class StatisticsReport(BaseModel):
    status: str  = Field(None,description="Status")
    data: str = Field(None,data="Data")


class Metrics(BaseModel):
    metrics :dict =  {
        '5GASP Network' : [
            'netdata_net_net_kilobits_persec_average{family="em1.557"}',
            'netdata_net_net_kilobits_persec_average{family="em2.557"}'],
        'UE PCI' : [
            'nas_value_nr5g_cell_information_physical_cell_id_868371050574256',
            'nas_value_nr5g_cell_information_physical_cell_id_868371050575170',
            'nas_value_nr5g_cell_information_physical_cell_id_868371050571278',
            'nas_value_nr5g_cell_information_physical_cell_id_868371050574348',
        ],
        'Indoor N3 interface' : [
            'abs(netdata_net_net_kilobits_persec_average{dimension="sent", family="enp3s0.557", instance="10.205.52.101:19999"}) * 8',
            'abs(netdata_net_net_kilobits_persec_average{instance="10.205.52.101:19999", family="enp3s0.557", dimension="received"}) * 8',
        ],
        'Outdoor N3 interface' : [
            'rate(collectd_snmp_if_octets_rx_total{snmp="te-1_1_6"}[1m]) * 8',
            'rate(collectd_snmp_if_octets_tx_total{snmp="te-1_1_6"}[1m]) * 8',
        ],
        'UEs TX/RX' : [
            'rate(wds_value_tx_bytes_ok_868371050574256{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_rx_bytes_ok_868371050574256{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_tx_bytes_ok_868371050575170{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_rx_bytes_ok_868371050575170{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_tx_bytes_ok_ 868371050571278{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_rx_bytes_ok_ 868371050571278{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_tx_bytes_ok_ 868371050574348{job="ue_statistics"}[1m]) * 8',
            'rate(wds_value_rx_bytes_ok_ 868371050574348{job="ue_statistics"}[1m]) * 8',
        ],
        'UEs RSRP' : [
            'nas_value_5g_signal_strength_rsrp_868371050574256',
            'nas_value_5g_signal_strength_rsrp_868371050575170',
            'nas_value_5g_signal_strength_rsrp_868371050571278',
            'nas_value_5g_signal_strength_rsrp_868371050574348'
        ]
}

    