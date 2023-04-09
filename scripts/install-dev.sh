# 
# # Install Dependencies
# Dev Mode - VLSIR comes from GitHub 
#

pwd
cd .. 
git clone -b dev https://github.com/Vlsir/Vlsir.git
cd Vlsir/bindings/python 
pip install -e .
cd ../../VlsirTools
pip install -e .
cd ../../Hdl21
pip install -e ".[dev]"
cd SampleSitePdks
pip install -e ".[dev]"
cd ../pdks/Sky130
pip install -e ".[dev]"

pre-commit install