import urllib2
import gp_emulator
from glob import glob
import os

class emulatorServer(object):
  '''
  helper class for accessing and using emulators
  '''

  def __init__(self,model='sail',database='my_data'):
    self.base = 'https://www.dropbox.com/sh/ljykiruevdakfh1/AADk4ywAvzyIleMy0c_e5dJNa?dl=0'
    # local storage
    self.database = database + '/' + model 
    # make directory if it doesnt exist
    if not os.path.exists(self.database):
      os.makedirs(self.database)
 
    # get a list of files available
    self.localFiles = glob(self.database+'/*.npz')
    try:
      f = urllib2.urlopen(self.base).readlines()

      self.remoteFiles = urllib2.urlopen(self.base) 
    except:
      print 'error accessing',self.url
      print 'using only local files from',self.database


  def grab_emulators (self, sza, vza, raa, i\
                    verbose=True,emulator_home = "emus/"):
    import glob
    # Locate all available emulators...
    files = glob.glob ( "%s.npz" % emulator_home )
    if len(files) == 0:
            files = glob.glob("%s*.npz" % emulator_home )
    emulator_search_dict = {}
    for f in files:
        ff = f.split('/')[-1].split('.')[0]
        try:
          emulator_search_dict[ float(ff.split("_")[0]), \
                              float(ff.split("_")[2]),
                              float(ff.split("_")[1]) - \
                              float(ff.split("_")[3])] = f
        except:
          emulator_search_dict[ \
                              float(ff.split("_")[1]),
                              float(ff.split("_")[2]) , \
                              float(ff.split("_")[3])] = f

    # So we have a dictionary inddexed by SZA, 
    # VZA and RAA and mapping to a filename
    emu_keys = np.array( emulator_search_dict.keys() )
    
    cemu_keys = np.cos(emu_keys*np.pi/180.).T
    semu_keys = np.sin(emu_keys*np.pi/180.).T
    cthis = np.cos(np.array([sza,vza,raa])*np.pi/180.)
    sthis = np.sin(np.array([sza,vza,raa])*np.pi/180.)
    # view vector
    v_xyzThis = np.array([sthis[0]*cthis[2],sthis[0]*sthis[2],cthis[0]])
    v_emu_keys = np.array([semu_keys[0]*cemu_keys[2],\
                        semu_keys[0]*semu_keys[2],cemu_keys[0]])
    # sun vector
    s_xyzThis = np.array([sthis[1],0.*sthis[0],cthis[1]])
    s_emu_keys = np.array([semu_keys[1],0.*semu_keys[1],cemu_keys[1]])
    vdist = np.dot(v_emu_keys.T,v_xyzThis)
    sdist = np.dot(s_emu_keys.T,s_xyzThis)
    # closest emulation point
    emu_locs = np.argmax(vdist+sdist,axis=0)

    emulators = {}
    for i in xrange(len(sza)):
        the_emu_key = emu_keys[emu_locs[i]]
        k = the_emu_key
        
        emulators[(int(k[0]), int(k[1]), int(k[2]))] = \
                gp_emulator.MultivariateEmulator \
                ( dump=emulator_search_dict[(k[0], k[1],k[2])])
        if verbose: print i,sza[i], vza[i], raa[i], \
                       k,emulator_search_dict[(k[0], k[1],k[2])]
    return emulators


  def read_modis_data ( self, fname ):
    '''
    simple ascii data input for testing
    '''
    d = np.loadtxt( fname)
    #QA_OK = np.array([1,8, 72, 136, 200, 1032, 1288, 2056, \
    #        2120, 2184,  2248])
    #qax =  np.logical_or.reduce([d[:,13]==x for x in QA_OK])
    qax = d[:,2] == 1
    # Already scaled
    #d[:,(2,3,4,5)] = d[:,(2,3,4,5)]/100.
    #d[:,6:] = d[:,6:]/10000.
    
    data = d[qax, :]
    doys = data[:,0]
    vza = data[:, 5]
    sza = data[:, 3]
    raa = data[:, 7]  
    return data, doys, vza, sza, raa
