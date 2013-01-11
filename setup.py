from setuptools import setup, find_packages


install_requires = ['Mako', 'docutils', 'Pygments', 'requests',
                    'rst2pdf', 'Pillow']


setup(name='FaitMain',
      version="0.1",
      url='https://github.com/tarekziade/boom',
      packages=find_packages(),
      description=("FaitMain Magazine"),
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      include_package_data=True,
      classifiers=[
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "License :: OSI Approved :: Apache Software License"],
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      faitmain = faitmain.generate:main
      """)
