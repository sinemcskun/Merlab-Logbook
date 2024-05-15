var sciField;

function showOptions() {
    sciField = document.getElementById('sciField');
    var labSelection = document.getElementById('labSelection');
    var machineSelection = document.getElementById('machineSelection');

    labSelection.innerHTML = '';
    machineSelection.innerHTML = '';

    var labOptions;
    var machineOptions;

    if (sciField.value === 'lifeSci') {
        labOptions = ['Moleküler Biyoloji ve Genetik Laboratuvarı', 'Optik/Floresan Mikroskopi Laboratuvarı', 'DNA-RNA Dizileme Laboratuvarı', 'Kromatografi ve Kütle Spektroskopi Laboratuvarı'];
        machineOptions = {
            'Moleküler Biyoloji ve Genetik Laboratuvarı': ['ABI STEP ONE PLUS REAL TIME PCR', 'QIAGEN ROTOR-GENE Q REAL TIME PCR','THERMO SCIENTIFIC NANODROP 2000C SPEKTROFOTOMETRE'],
            'Optik/Floresan Mikroskopi Laboratuvarı': ['LEICA DM3000 FLORESAN MİKROSKOP', 'OLYMPUS CKX41 İNVERTED FLUORESAN MİKROSKOP'],
            'DNA-RNA Dizileme Laboratuvarı': ['ION S5™ YENİ NESİL DİZİLEME SİSTEMİ', 'APPLIED BIOSYSTEMS 3500 GENETIC ANALYZER'],
            'Kromatografi ve Kütle Spektroskopi Laboratuvarı': ['SCIEX TRIPLE QUADRUPOLE 3500 LC-MS/MS SİSTEMİ', 'THERMO SCIENTIFIC TSQ DUO TRIPLE QUADRUPOLE GC-MS/MS']

        };
    } else if (sciField.value === 'engSci') {
        labOptions = ['Elektron Mikroskopi Laboratuvarı', 'Termal Analiz Laboratuvar', 'Raman, Floresan, Uv-Vis, NIR Spektroskopi Laboratuvarı'];
        machineOptions = {
            'Elektron Mikroskopi Laboratuvarı': ['HITACHI SU5000 ALAN EMİSYONLU TARAMALI ELEKTRON MİKROSKOPU (FE-SEM)'],
            'Termal Analiz Laboratuvar': ['LINSEIS HFM 300/3 TERMAL İLETKENLİK ANALİZ CİHAZI', 'LINSEIS LFA 1000 LAZER FLAŞ ISIL İLETKENLİK/ISIL YAYILIM KATSAYISI ANALİZ CİHAZI', 'ULVAC ZEM-3M10 SEEBECK / ELEKTRİKSEL ÖZDİRENÇ KATSAYISI ÖLÇÜM CİHAZI','HITACHI STA 7300 EŞZAMANLI TERMOGRAVİMETRİ / DİFERANSİYEL TERMAL ANALİZ (TG/DTA) CİHAZI','HITACHI DSC 7020 DİFERANSİYEL TARAMALI KALORİMETRE (DSC)'],
            'Raman, Floresan, Uv-Vis, NIR Spektroskopi Laboratuvarı': ['JASCO NRS4500 KONFOKAL MİKROSKOPLU RAMAN SPEKTROMETRE'],
        };
    }

    for (var i = 0; i < labOptions.length; i++) {
        var option = document.createElement('option');
        option.value = labOptions[i];
        option.textContent = labOptions[i]; // Lab ismi olarak özel ismi kullan
        labSelection.appendChild(option);
    }

    showMachineOptions();
}

var selectedTemplate;
var selectedParamCount;


function showMachineOptions() {
    var labSelection = document.getElementById('labSelection');
    var machineSelection = document.getElementById('machineSelection');

    var selectedLab = labSelection.value;
    var machineOptions;

    if (sciField.value === 'lifeSci') {
        machineOptions = {
            'Moleküler Biyoloji ve Genetik Laboratuvarı': ['ABI STEP ONE PLUS REAL TIME PCR', 'QIAGEN ROTOR-GENE Q REAL TIME PCR','THERMO SCIENTIFIC NANODROP 2000C SPEKTROFOTOMETRE'],
            'Optik/Floresan Mikroskopi Laboratuvarı': ['LEICA DM3000 FLORESAN MİKROSKOP', 'OLYMPUS CKX41 İNVERTED FLUORESAN MİKROSKOP'],
            'DNA-RNA Dizileme Laboratuvarı': ['ION S5™ YENİ NESİL DİZİLEME SİSTEMİ', 'APPLIED BIOSYSTEMS 3500 GENETIC ANALYZER'],
            'Kromatografi ve Kütle Spektroskopi Laboratuvarı': ['SCIEX TRIPLE QUADRUPOLE 3500 LC-MS/MS SİSTEMİ', 'THERMO SCIENTIFIC TSQ DUO TRIPLE QUADRUPOLE GC-MS/MS']

        };
    } else if (sciField.value === 'engSci') {
        machineOptions = {
            'Elektron Mikroskopi Laboratuvarı': ['HITACHI SU5000 ALAN EMİSYONLU TARAMALI ELEKTRON MİKROSKOPU (FE-SEM)'],
            'Termal Analiz Laboratuvar': ['LINSEIS HFM 300/3 TERMAL İLETKENLİK ANALİZ CİHAZI', 'LINSEIS LFA 1000 LAZER FLAŞ ISIL İLETKENLİK/ISIL YAYILIM KATSAYISI ANALİZ CİHAZI', 'ULVAC ZEM-3M10 SEEBECK / ELEKTRİKSEL ÖZDİRENÇ KATSAYISI ÖLÇÜM CİHAZI','HITACHI STA 7300 EŞZAMANLI TERMOGRAVİMETRİ / DİFERANSİYEL TERMAL ANALİZ (TG/DTA) CİHAZI','HITACHI DSC 7020 DİFERANSİYEL TARAMALI KALORİMETRE (DSC)'],
            'Raman, Floresan, Uv-Vis, NIR Spektroskopi Laboratuvarı': ['JASCO NRS4500 KONFOKAL MİKROSKOPLU RAMAN SPEKTROMETRE'],
        };
    }

    machineSelection.innerHTML = '';

    if (machineOptions && machineOptions[selectedLab]) {
        for (var j = 0; j < machineOptions[selectedLab].length; j++) {
            var option = document.createElement('option');
            option.value = machineOptions[selectedLab][j];
            option.textContent = machineOptions[selectedLab][j];
            machineSelection.appendChild(option);
        }

        selectedTemplate = machineOptions[selectedLab];
        selectedParamCount = selectedTemplate.length;
    }
    updateFormAction();
}
