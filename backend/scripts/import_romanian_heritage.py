"""
Script to import Romanian heritage data from INP (Institutul Național al Patrimoniului)
Usage: python scripts/import_romanian_heritage.py
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rdf_store import RDFStoreService
from app.services.data_importer import DataImporter
import structlog

logger = structlog.get_logger()

INP_URLS = {
    'lmi_edm': 'https://data.gov.ro/dataset/99abe8fa-522b-4175-9349-98fb8473c6fd/resource/853e4157-c73f-4713-9f6e-a472e5cad1b1/download/inp-lmh-edm.xml',
}


async def main():
    """Import Romanian heritage data"""
    
    print("=" * 60)
    print("Romanian Heritage Data Importer")
    print("=" * 60)
    
    print("\n1. Initializing RDF store...")
    rdf_service = RDFStoreService()
    await rdf_service.initialize()
    print(f"   ✓ RDF store initialized with {len(rdf_service.graph)} triples")
    
    importer = DataImporter(rdf_service)
    
    total_imported = 0
    total_errors = 0
    
    for dataset_name, url in INP_URLS.items():
        print(f"\n2. Importing dataset: {dataset_name}")
        print(f"   URL: {url}")
        
        try:
            result = importer.import_from_url(url, format="edm")
            
            print(f"   ✓ Successfully imported: {result['imported']} items")
            if result['errors'] == 0:
                print(f"   ✓ No errors encountered")
            else:
                print(f"   ✗ Errors: {result['errors']}")
            
            if result['error_details']:
                print("\n   First few errors:")
                for error in result['error_details'][:3]:
                    print(f"     - {error}")
            
            total_imported += result['imported']
            total_errors += result['errors']
            
        except Exception as e:
            print(f"   ✗ Failed to import {dataset_name}: {e}")
            total_errors += 1
    
    print("\n3. Saving RDF data...")
    print(f"   Total triples to save: {len(rdf_service.graph)}")
    output_file = "data/romanian_heritage.nt"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        print(f"   Serializing graph to {output_file} (N-Triples format for speed)...")
        rdf_service.save_to_file(output_file, format="nt")
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"   ✓ Saved to: {output_file}")
            print(f"   ✓ File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
        else:
            print(f"   ✗ File was not created: {output_file}")
    except Exception as e:
        print(f"   ✗ Error saving file: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total imported: {total_imported}")
    print(f"Total errors: {total_errors}")
    print(f"Total triples: {len(rdf_service.graph)}")
    print(f"Output file: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
