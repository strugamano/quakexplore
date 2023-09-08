"""

Earthquake data provided by USGS, accessed through API

    https://earthquake.usgs.gov/fdsnws/event/1/
    https://earthquake.usgs.gov/data/comcat/index.php
    
The GEOJson data format:

    https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson_detail.php
    https://geojson.org/
    https://geojson.io/#map=5.76/46.624/19.405

Python and APIs:

    https://realpython.com/python-api/

    > python -m pip install requests

"""

import sys

from requests import get
from time import strftime, gmtime

from PySide6.QtCore import Qt, QSize, QDate, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QGridLayout, QAbstractItemView,
    QStatusBar, QToolBar, QLabel, QDoubleSpinBox, QDateEdit, QTableWidget, QTableWidgetItem, QSpacerItem, QPushButton)

api_url = "https://earthquake.usgs.gov/fdsnws/event/1/"

sources = {
    'ak': "Alaska Earthquake Center", 'at': "National Tsunami Warning Center", 'atlas': "ShakeMap Atlas",
    'av': "Alaska Volcano Observatory", 'cdmg': "cdmg", 'cgs': "cgs",
    'choy': "Energy Magnitude and Broadband Depth", 'ci': "California Integrated Seismic Network", 'duputel': "Duputel et al. W phase catalog",
    'eqh': "EQH - Coffman, von Hake and Stover, Earthquake History of the United States", 'gcmt': " Lamont-Doherty Earth Observatory", 'hv': "Hawaii Volcano Observatory",
    'iscgem': "ISC-GEM Main Catalog", 'iscgemsup': "ISC-GEM Supplementary Catalog", 'ismpkansas': "USGS Induced Seismicity Project (Kansas)",
    'ld': "Lamont-Doherty Cooperative Seismographic Network", 'mb': "Montana Bureau of Mines and Geology", 'nc': "California Integrated Seismic Network: Northern California Seismic System",
    'nm': "New Madrid Seismic Network", 'nn': "Nevada Seismological Laboratory", 'official': "USGS Earthquake Magnitude Working Group",
    'ok': "ok", 'pr': "Puerto Rico Seismic Network", 'pt': "Pacific Tsunami Warning Center",
    'sc': "sc", 'se': "Center for Earthquake Research and Information", 'us': "USGS National Earthquake Information Center, PDE",
    'ushis': "USHIS - Stover and Coffman, Seismicity of the United States, 1568-1989", 'uu': "University of Utah Seismograph Stations", 'uw': "Pacific Northwest Seismic Network"
}

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        

    # INIT
        self.setWindowTitle("quakexplore")
        self.setFixedSize(QSize(1200, 700))
        layout = QVBoxLayout()

        spacer = QWidget() # spacer for widgets
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # STATUSBAR
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.quake_count = dValue()
        self.quake_count.v = 0
        self.quake_count.changed.connect(lambda value: self.update_statusbar(value, "quakes listed."))
        
    # TOOLBAR
        self.toolbar = QToolBar("main toolbar")
        self.toolbar.setIconSize(QSize(32,32))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)

        # QUERY
        query_action = QAction(QIcon('res/go-down-skip.svg'), "Start query", self)
        #query_action.setStatusTip("Start query...")
        query_action.triggered.connect(self.query_action)
        self.toolbar.addAction(query_action)

        # DETAILS
        self.event_page_action = QAction(QIcon('res/usgs-logo-circle-transparent.png'), "Open USGS event page", self)
        self.event_page_action.triggered.connect(self.open_event_page)
        self.toolbar.addAction(self.event_page_action)
        self.event_page_action.setVisible(False)

        # <--- left side
        self.toolbar.addWidget(spacer)
        # right side --->

        # ABOUT
        about_action = QAction(QIcon('res/help-about.svg'), "About", self)
        about_action.triggered.connect(self.about_action)
        self.toolbar.addAction(about_action)

        # EXIT
        exit_action = QAction(QIcon('res/window-close.svg'), "Exit", self)
        exit_action.triggered.connect(self.exit_action)
        self.toolbar.addAction(exit_action)

    # |------------------------------------|
    # |----- INPUT ------------------------|
    # |------------------------------------|

    # FILTERS
        filters_layout = QGridLayout()
        filters_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed), 0, 3)

        # MAGNITUDE SPINBOXES
        self.min_magnitude_spinbox = QDoubleSpinBox()
        self.min_magnitude_spinbox.setRange(0,10)
        self.min_magnitude_spinbox.setSingleStep(0.1)
        self.min_magnitude_spinbox.setFixedWidth(70)
        self.min_magnitude_spinbox.setValue(6.0)
        self.min_magnitude_spinbox.valueChanged.connect(self.min_magnitude_spinbox_value_changed)
        self.min_magnitude_label = QLabel(f"min magnitude: {self.min_magnitude_spinbox.value()}")
        filters_layout.addWidget(self.min_magnitude_spinbox, 0, 0)
        filters_layout.addWidget(self.min_magnitude_label, 0, 1)

        self.max_magnitude_spinbox = QDoubleSpinBox()
        self.max_magnitude_spinbox.setRange(0,10)
        self.max_magnitude_spinbox.setSingleStep(0.1)
        self.max_magnitude_spinbox.setFixedWidth(70)
        self.max_magnitude_spinbox.setValue(10.0)
        self.max_magnitude_spinbox.valueChanged.connect(self.max_magnitude_spinbox_value_changed)
        self.max_magnitude_label = QLabel(f"max magnitude: {self.max_magnitude_spinbox.value()}")
        filters_layout.addWidget(self.max_magnitude_spinbox, 1, 0)
        filters_layout.addWidget(self.max_magnitude_label, 1, 1)

        # DATE
        self.start_date = QDateEdit()
        self.start_date.setFixedWidth(100)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.start_date_changed)
        start = f"{self.start_date.date().year()}-{self.start_date.date().month()}-{self.start_date.date().day()}"
        self.start_date_label = QLabel(f"start date: {start}")
        filters_layout.addWidget(self.start_date, 0, 2)
        filters_layout.addWidget(self.start_date_label, 0, 3)

        self.end_date = QDateEdit()
        self.end_date.setFixedWidth(100)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.end_date_changed)
        end = f"{self.end_date.date().year()}-{self.end_date.date().month()}-{self.end_date.date().day()}"
        self.end_date_label = QLabel(f"end date: {end}")
        filters_layout.addWidget(self.end_date, 1, 2)
        filters_layout.addWidget(self.end_date_label, 1, 3)

        layout.addLayout(filters_layout)

    # |------------------------------------|
    # |----- OUTPUT -----------------------|
    # |------------------------------------|

        output_layout = QHBoxLayout()

    # DATA
        data_layout = QVBoxLayout()
        data_layout.setSpacing(1)
        data_layout.setContentsMargins(1, 1, 1, 1)
        self.data = QWidget()
        self.data.setLayout(data_layout)
        output_layout.addWidget(self.data)

        # DATALIST
        self.quakes = []
        self.datalist = QTableWidget()
        #self.datalist.setReadOnly(True)
        """ self.data.setOpenExternalLinks(True)
        self.data.setOpenLinks(False)
        self.data.anchorClicked.connect(QDesktopServices.openUrl) """
        self.datalist.setFixedWidth(700)
        self.datalist.setShowGrid(False)
        self.datalist.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.datalist.setEditTriggers(QTableWidget.NoEditTriggers)
        #self.datalist.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.datalist.setColumnCount(6)
        self.datalist.setColumnHidden(5, True) # id is disabled by default!
        self.datalist.setColumnWidth(0, 110)
        self.datalist.setColumnWidth(1, 90)
        self.datalist.setColumnWidth(2, 70)
        self.datalist.setColumnWidth(3, 95)
        self.datalist.setColumnWidth(4, 315)
        
        self.datalist.setSortingEnabled(True)
        self.datalist.verticalHeader().setVisible(False)
        self.datalist.setHorizontalHeaderLabels(["datetime", "magnitude", "depth", "significance", "location", "id"]) # id is disabled by default!
        self.datalist.horizontalHeader().sortIndicatorChanged.connect(self.sort_quakes)
        self.datalist.currentItemChanged.connect(self.show_quake_details)

        data_layout.addWidget(self.datalist)

    # DETAILS
        details_layout = QVBoxLayout()
        self.details = QWidget()
        self.details.setFixedWidth(450)
        self.details.setLayout(details_layout)
        output_layout.addWidget(self.details)        

        self.detail_summary = QLabel()
        self.detail_location = QLabel()
        self.detail_felt = QLabel()
        self.detail_updated = QLabel()
        self.detail_intensity = QLabel()
        self.detail_intensity.setOpenExternalLinks(True)
        self.detail_alert = QLabel()
        self.detail_alert.setOpenExternalLinks(True)
        self.detail_status = QLabel()
        self.detail_net = QLabel()
        self.detail_net.setOpenExternalLinks(True)
        self.detail_ids = QPushButton("Associated events")
        self.detail_ids.clicked.connect(self.show_ids)
        self.detail_ids.setVisible(False)

        details_layout.addWidget(self.detail_summary)
        details_layout.addWidget(self.detail_location)
        details_layout.addWidget(self.detail_felt)
        details_layout.addWidget(self.detail_intensity)
        details_layout.addWidget(self.detail_alert)
        details_layout.addWidget(self.detail_net)
        details_layout.addWidget(self.detail_ids)
        details_layout.addStretch()
        details_layout.addWidget(self.detail_status)
        details_layout.addWidget(self.detail_updated)
        
        layout.addLayout(output_layout)

    # |------------------------------------|
        
    # test query: api version
        """ try:
            api_endpoint = "version"
            version = get(api_url + api_endpoint).text
            print("USGS API version:", version)
            self.status_bar.showMessage("USGS API version: " + version)
        except ConnectionError as err: print("Connection error:", err) """

    # CONTAINER
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # |------------------------------------|
    # |----- SLOTS ------------------------|
    # |------------------------------------|

    @Slot() # reusable statusbar updater
    def update_statusbar(self, value, text): self.status_bar.showMessage(f"{value} {text}")

    @Slot() # exit
    def exit_action(self): sys.exit('Goodbye!')

    @Slot() # about
    def about_action(self):
        print('About...')

    @Slot() # sorting quakes when table is sorted
    def sort_quakes(self, i, o):
        keys = {0: 'datetime', 1: 'magnitude', 2: 'depth', 3: 'significance'}
        index = keys[i]
        order = 'asc.' if o == Qt.AscendingOrder else 'desc.'
        print(f"Sorting quakes by {index} ({order})")

        if index == 'datetime': self.quakes.sort(key=lambda s: s['datetime'], reverse=True if o == Qt.DescendingOrder else False)
        elif index == 'magnitude': self.quakes.sort(key=lambda s: s['props']['mag'], reverse=True if o == Qt.DescendingOrder else False)
        elif index == 'depth': self.quakes.sort(key=lambda s: s['geometry']['coordinates'][2], reverse=True if o == Qt.DescendingOrder else False)
        else: self.quakes.sort(key=lambda s: s['props']['sig'], reverse=True if o == Qt.DescendingOrder else False)

    @Slot() # start and list query
    def query_action(self):
        min_mag = f"{self.min_magnitude_spinbox.value():.1f}"
        max_mag = f"{self.max_magnitude_spinbox.value():.1f}"
        start = f"{self.start_date.date().year()}-{self.start_date.date().month()}-{self.start_date.date().day()}"
        end = f"{self.end_date.date().year()}-{self.end_date.date().month()}-{self.end_date.date().day()}"
        api_endpoint = f"query?format=geojson&orderby=time&starttime={start}&endtime={end}&minmagnitude={min_mag}&maxmagnitude={max_mag}"
        
        print(f"Query: {api_url}{api_endpoint}\n  > Filters - min: {min_mag} max: {max_mag} start: {start} end: {end}")
        self.details.setVisible(False)
        self.event_page_action.setVisible(False)
                
        data = get(api_url + api_endpoint).json()
        row = 0
        self.quakes = []
        self.datalist.clearContents()
        self.datalist.setFocus()
        self.datalist.setRowCount(data['metadata']['count'])
        self.datalist.sortItems(0, Qt.DescendingOrder)
        
        for quake in data['features']:
            props = quake['properties']

            datetime = strftime("%y-%m-%d %H:%M:%S", gmtime(int(props['time']/1000)))
            datetime_item = QTableWidgetItem(datetime)
            datetime_item.setTextAlignment(Qt.AlignCenter)

            mag = f"{props['mag']:.1f}"
            mag_item = QTableWidgetItem()
            mag_item.setTextAlignment(Qt.AlignCenter)
            mag_item.setData(Qt.DisplayRole, float(f"{props['mag']:.1f}"))
            
            depth = f"{quake['geometry']['coordinates'][2]:.1f}"
            depth_item = QTableWidgetItem()
            depth_item.setTextAlignment(Qt.AlignCenter)
            depth_item.setData(Qt.DisplayRole, float(f"{quake['geometry']['coordinates'][2]:.1f}"))

            sig_item = QTableWidgetItem()
            sig_item.setTextAlignment(Qt.AlignCenter)
            sig_item.setData(Qt.DisplayRole, props['sig'])
            
            label = f"{datetime:<17}{mag:^11}{depth:^11}{props['place']}"
            
            self.datalist.setItem(row, 0, datetime_item)
            self.datalist.setItem(row, 1, mag_item)
            self.datalist.setItem(row, 2, depth_item)
            self.datalist.setItem(row, 3, sig_item)
            self.datalist.setItem(row, 4, QTableWidgetItem(f"{props['place']}"))
            self.datalist.setItem(row, 5, QTableWidgetItem(f"{quake['id']}"))

            row += 1
            self.quakes.append({
                'id': quake['id'],
                'label': label,
                'datetime': datetime,
                'props': props,
                'geometry': quake['geometry']
            })

        min_sig = min(q['props']['sig'] for q in self.quakes)
        max_sig = max(q['props']['sig'] for q in self.quakes)
        
        # another option for choosing min/max:
        #max_sig = max(self.quakes, key=lambda x:x['props']['sig'])
        #min_sig = min(self.quakes, key=lambda x:x['props']['sig'])

        for row in range(self.datalist.rowCount()):
            alpha = int(255*((self.quakes[row]['props']['sig'] - min_sig) / ((max_sig - min_sig)*0.01))*0.01)
            for column in range(self.datalist.columnCount()): self.datalist.item(row, column).setBackground(QBrush(QColor(255, 153, 51, alpha)))

        self.quakes.sort(key=lambda s: s['datetime'], reverse=True)
        self.quake_count.v = data['metadata']['count']
        print(f"{data['metadata']['count']} quakes. Maximal/minimal significance: {max_sig}/{min_sig} - Done.")

    @Slot() # show quake details
    def show_quake_details(self, quake):
        if self.datalist.currentRow() == -1: pass
        else:
            self.datalist.setFocus()
            self.details.setVisible(True)
            self.event_page_action.setVisible(True)
            self.detail_intensity.setVisible(True)
            self.detail_alert.setVisible(True)
            quake = self.quakes[quake.row()]
            print(f"Show quake details: {quake['id']}, significance: {quake['props']['sig']}\n  > {quake['label']}\n  > Associated events ({quake['props']['ids'].count(',') - 1}): {quake['props']['ids'].strip(',').split(',')}")

            self.detail_summary.setText(f"{quake['props']['mag']} magnitude quake, {quake['geometry']['coordinates'][2]:.1f} kms deep @ {quake['datetime']}")

            self.detail_location.setText(f"{quake['props']['place'] if quake['props']['place'] else 'Unknown location'}")

            self.detail_felt.setText("Nobody felt it." if not quake['props']['felt'] else f"Felt by {quake['props']['felt']} people.")

            if quake['props']['cdi'] and quake['props']['mmi']: self.detail_intensity.setText(f"Intensity: {quake['props']['cdi']} (<a href='https://earthquake.usgs.gov/data/dyfi/'>DYFI</a>), {quake['props']['mmi']} (<a href='https://earthquake.usgs.gov/data/shakemap/'>ShakeMap</a>)")
            elif quake['props']['cdi'] or quake['props']['mmi']: self.detail_intensity.setText(f"Intensity: {quake['props']['cdi']} (<a href='https://earthquake.usgs.gov/data/dyfi/'>DYFI</a>)") if quake['props']['cdi'] else self.detail_intensity.setText(f"Intensity: {quake['props']['mmi']} (<a href='https://earthquake.usgs.gov/data/shakemap/'>ShakeMap</a>)")
            else: self.detail_intensity.setVisible(False)

            self.detail_alert.setText(f"<a href='https://earthquake.usgs.gov/data/pager/'>PAGER</a> alert level: <font color='{quake['props']['alert']}'>{quake['props']['alert']}</font>") if quake['props']['alert'] else self.detail_alert.setVisible(False)
            self.detail_net.setText(f"Preferred source: <a href='https://earthquake.usgs.gov/data/comcat/catalog/{quake['props']['net']}/'>{sources[quake['props']['net']]}</a>")
            self.detail_ids.setVisible(False) if (quake['props']['ids'].count(",") == 2 and quake['props']['ids'].strip(",") == quake['id']) or (quake['props']['ids'].count(",") == 3 and "usauto" in quake['props']['ids']) else self.detail_ids.setVisible(True)

            # ...
            
            self.detail_status.setText(f"<font color='{'green' if quake['props']['status'] == 'reviewed' else 'yellow'}'>{quake['props']['status'].upper()}</font>")
            self.detail_updated.setText(f"(last update: {strftime('%y-%m-%d %H:%M:%S', gmtime(int(quake['props']['updated']/1000)))})")

    @Slot() # show associated events
    def show_ids(self):
        self.datalist.setFocus()
        quake = self.quakes[self.datalist.currentRow()]
        print(f"{quake['id']} - associated events ({quake['props']['ids'].count(',') - 1}): {quake['props']['ids'].strip(',').split(',')}")

    @Slot() # open quake details
    def open_event_page(self):
        self.datalist.setFocus()
        quake = self.quakes[self.datalist.currentRow()]
        print(f"Open quake details: {quake['label']} - id: {quake['id']}\n  > url: {quake['props']['url']}")
        QDesktopServices.openUrl(quake['props']['url'])

    @Slot() # minimum magnitude
    def min_magnitude_spinbox_value_changed(self, value):
        print(f"Minimal magnitude: {value:.1f}")
        self.min_magnitude_label.setText(f"min magnitude: {value:.1f}")

    @Slot() # maximum magnitude
    def max_magnitude_spinbox_value_changed(self, value):
        print(f"Maximal magnitude: {value:.1f}")
        self.max_magnitude_label.setText(f"max magnitude: {value:.1f}")

    @Slot() # start date
    def start_date_changed(self):
        date = f"{self.start_date.date().year()}-{self.start_date.date().month()}-{self.start_date.date().day()}"
        print(f"Start date: {date}")
        self.start_date_label.setText(f"start date: {date}")

    @Slot() # end date
    def end_date_changed(self):
        date = f"{self.end_date.date().year()}-{self.end_date.date().month()}-{self.end_date.date().day()}"
        print(f"End date: {date}")
        self.end_date_label.setText(f"end date: {date}")

class dValue(QWidget): # for dynamic variables that emit a signal when its value has been changed
    changed = Signal(int)

    def __init__(self, parent=None):
        super(dValue, self).__init__(parent)
        self._v = 0

    @property
    def v(self):
        return self._v

    @v.setter
    def v(self, value):
        self._v = value
        self.changed.emit(value)


app = QApplication(sys.argv)

# test query: api version
try:
    window = MainWindow()
    window.show()
    api_endpoint = "version"
    version = get(api_url + api_endpoint).text
    print(f"USGS API version: {version}")
    window.status_bar.showMessage(f"USGS API version: {version}")
    app.exec()
except ConnectionError as err: print(f"Connection error: {err}")

print("Goodbye!")
