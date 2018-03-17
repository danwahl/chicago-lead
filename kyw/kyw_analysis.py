import pandas as pd
import numpy as np
import nvector as nv
import best
import best.plot
from pymc import MCMC

MAX_DISTANCE = 50.0

if __name__ == '__main__':
    # read main replacements
    cip = pd.read_csv('cip.csv', index_col='bes', parse_dates=['start', 'end'])
    
    # read water quality tests
    wq = pd.read_csv('wq.csv', index_col='date', parse_dates=['date'])
    
    # nav frame
    frame = nv.FrameE(a=6371e3, f=0)
    
    data = []

    for j in range(len(wq)):
        # get water test point
        p1 = frame.GeoPoint(wq.iloc[j]['lat'], wq.iloc[j]['lng'], degrees=True)
    
        for i in range(len(cip)):
            # get main replacement path
            l1 = frame.GeoPoint(cip.iloc[i]['from_lat'], cip.iloc[i]['from_lng'], degrees=True)
            l2 = frame.GeoPoint(cip.iloc[i]['to_lat'], cip.iloc[i]['to_lng'], degrees=True)
            path = nv.GeoPath(l1, l2)
                        
            # calculate distance
            d = path.cross_track_distance(p1, method='greatcircle').ravel()
            if np.abs(d[0]) <= MAX_DISTANCE:
                p2 = path.closest_point_on_great_circle(p1)
                
                # check if on path, append and break (only line per water test)
                if path.on_path(p2)[0]:
                    data.append({
                        'p1_lat': p1.latitude_deg,
                        'p1_lng': p1.longitude_deg,
                        'p2_lat': p2.latitude_deg[0],
                        'p2_lng': p2.longitude_deg[0],
                        'd': d[0],
                        'date': wq.index[j],
                        'val': wq.iloc[j][['1st', '4th', '6th', '5min', '5min2']].max(),
                        'study': wq.iloc[j]['study'],
                        'bes': cip.index[i],
                        'start': cip.iloc[i]['start'],
                        'actual_start': cip.iloc[i]['actual_start'],
                        'end': cip.iloc[i]['end'],
                        'actual_end': cip.iloc[i]['actual_end'],
                        'in_house': cip.iloc[i]['in_house'],
                        'length': cip.iloc[i]['length']
                    })
                    break;
    
    test = pd.DataFrame(data)
    test.to_csv('test.csv')

    # run "best" analysis
    after = test[(test['date'] > test['end']) & test['actual_end'] & test['study']]['val']
    before = test[(test['date'] < test['start']) & test['actual_start'] & test['study']]['val']

    model = best.make_model({'before': before.tolist(), 'after': after.tolist()})
    
    M = MCMC(model)
    M.sample(iter=110000, burn=10000)
    
    fig = best.plot.make_figure(M)
    fig.savefig('best.png', dpi=70)