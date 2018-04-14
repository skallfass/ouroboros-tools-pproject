<table style="text-align: left; font-size: 18px">
    <tr>
        <td>Twitter</td>
        <td>@simon\_kallfass</td>
    </tr>
    <tr>
        <td>GitHub</td>
        <td>skallfass</td>
    </tr>
    <tr>
        <td>GitLab</td>
        <td>skallfass</td>
    </tr>
    <tr>
        <td>LinkedIn</td>
        <td>Simon Kallfaß</td>
    </tr>
    <tr>
        <td>Homepage</td>
        <td>[www.ouroboros.info](https://www.ouroboros.info)</td>
    </tr>
</table>

<img src="https://pproject.ouroboros.info/_images/pproject.svg" alt="pproject logo" width="30%" height="30%" z-index=-5 style="background-color: #434344;">

[www.pproject.ouroboros.info](https://www.pproject.ouroboros.info)

---
## Warum pproject?
* Vereinfachung von
    * Entwicklung in Conda-Environments
    * Ausrollen als Conda-Packages
* VCS
    * Repository anlegen
    * git-tags
* feste Projektstruktur
    * gleicher Aufbau
    * vorhersehbarer Inhalt
* als Playground für Packages & Technologien

---
## Features
* Shell-tool (bash und zsh)
* Projekterstellung (lokal / remote)
* Conda-Environments (erstellen und updaten)
* Tests (pytest)
* Conda-Packages
* Rollout (als Conda-Package in eigenem Conda-Env)
* Sphinx

---
### Workflow
<img src="https://www.pproject.ouroboros.info/_images/pproject_workflow_new.svg" alt="Workflow" width="65%" height="65%">

---
## Resultierende Projektstruktur
```
├── conda-build
│       ├── meta.yaml
│       └── hash.md5
├── company
│       ├── init__.py
│       └── namespace
│           ├── init__.py
│           └── project
│               ├── your_code.py
│               └── __init__.py
├── .git
├── README.md
├── setup.py
└── tests
```

---
## autoenv und autoupdate
autoenv aktivieren
```bash
pproject autoenv_toggle
```
autoupdate aktivieren
```bash
pproject autoupdate_toggle
```
auto-commands ausführen
```bash
pproject autoenv
```

---
## Erstellen und Entwickeln
Projekt erstellen
```bash
pproject create [--remote] NAMESPACE -n PROJECT [-p {2.7, 3.6}]
```
Update des Conda-Environment
```bash
pproject update
```
Testen
```bash
pproject test
```

---
## Info und Build
Überblick
```bash
pproject info {project, general}
```
Neuer Versionstag
```bash
pproject version -m "MESSAGE" {major, minor, patch}
```
Conda-Package erstellen
```bash
pproject build [--publish]
```

---
## Ausrollen und Dokumentation
Ausrollen auf Host
```bash
pproject release -d USER@HOST [-e ENVIRONMENT_NAME]
```
Erstellen der Sphinx-Dokumentation
```bash
pproject sphinx
```

---
## Example: pproject create

[![Example](https://asciinema.org/a/6IOIgrb6mFjNPKggsAHEbQRNH.png)](https://asciinema.org/a/6IOIgrb6mFjNPKggsAHEbQRNH)

---
## Example: pproject test/version

[![Example](https://asciinema.org/a/ZLFmODNFCwMNCfqo1QHGapjec.png)](https://asciinema.org/a/ZLFmODNFCwMNCfqo1QHGapjec)

---
## Roadmap
* flexiblere Namespaces (Plugin-System?)
* CI-Skeletons
* Neuer Befehl: "containerize/dockerize/..."
* eventuell Bitbucket-support
* fish-support

---
## Contributors welcome!
<table style="text-align: left; font-size: 18px">
    <tr>
        <td>Homepage</td>
        <td>https://www.pproject.ouroboros.info</td>
    </tr>
    <tr>
        <td>GitHub</td>
        <td>skallfass/ouroboros-tools-pproject</td>
    </tr>
    <tr>
        <td>GitLab</td>
        <td>ouroboros-tools/pproject</td>
    </tr>
</table>
