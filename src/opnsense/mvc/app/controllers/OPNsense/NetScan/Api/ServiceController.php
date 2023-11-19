<?php

namespace OPNsense\NetScan\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

class ServiceController extends ApiControllerBase
{
    public function searchAction()
    {
        $this->sessionClose();

        $response = (new Backend())->configdpRun('netscan list');

        $parsed = json_decode($response, true);

        return $this->searchRecordsetBase($parsed);
    }

    public function getNameAction($mac = null)
    {
        $response = (new Backend())->configdpRun('netscan gethost', $mac);

        return json_decode($response, true);
    }

    public function setNameAction($mac)
    {
        $netscan = json_decode(file_get_contents('php://input'), true);
        $h = json_encode($netscan["netscan"]);

        $response = (new Backend())->configdpRun('netscan sethost', $h);

        return array("result" => "saved");
    }
}
