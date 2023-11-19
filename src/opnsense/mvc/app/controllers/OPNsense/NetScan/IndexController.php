<?php

namespace OPNsense\NetScan;

class IndexController extends \OPNsense\Base\IndexController
{
    public function indexAction()
    {
        // pick the template to serve to our users.
        $this->view->pick('OPNsense/NetScan/index');
        $this->view->formDialogNetScan = $this->getForm("dialogNetScan");
    }
}
