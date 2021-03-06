#
# Collective Knowledge: crowdbenchmarking using ARM's workload automation and CK
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
rrepo='upload' # TBD - get from cfg

compiler_choices='#choices#compiler_flags#'

line='================================================================'

fsummary='summary.json'
fclassification='classification.json'
fgraph='tmp-reactions-graph.json'
ffstat='ck-stat-flat-characteristics.json'

form_name='wa_web_form'
onchange='document.'+form_name+'.submit();'

hextra='<i><center>\n'
hextra+='This is an on-going long-term scenario. Please check our vision [ '
hextra+='<a href="http://doi.acm.org/10.1145/2909437.2909449">IWOCL\'16</a>, \n'
hextra+='<a href="http://arxiv.org/abs/1506.06256">CPC\'15</a>, \n'
hextra+='<a href="https://www.youtube.com/watch?v=Q94yWxXUMP0">YouTube</a>, \n'
hextra+='<a href="http://ctuning.org/cm/wiki/index.php?title=CM:data:45741e3fbcf4024b:1db78910464c9d05">wiki</a> ] '
hextra+=' and <a href="https://github.com/dividiti/ck-caffe">CK-Caffe GitHub repo</a> for more details!'
hextra+='</center></i>\n'
hextra+='<br>\n'

selector=[{'name':'Scenario', 'key':'crowd_uid', 'module_uoa':'65477d547a49dd2c', 'module_key':'##dict#title'},
          {'name':'Platform', 'key':'plat_name'},
          {'name':'CPU', 'key':'cpu_name', 'new_line':'yes'},
          {'name':'OS', 'key':'os_name'},
          {'name':'GPU', 'key':'gpu_name'}]

abis=[{'abi':'arm64-v8a',
       'os_uoa':'android21-arm64'},
      {'abi':'armeabi-v7a',
       'os_uoa':'android21-arm-v7a'}]

libcaffe='libcaffe.so'
libxopenme='librtlxopenme.so'

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# show results

def show(i):
    """
    Input:  {
               (crowd_module_uoa) - if rendered from experiment crowdsourcing
               (crowd_key)        - add extra name to Web keys to avoid overlapping with original crowdsourcing HTML
               (crowd_on_change)  - reuse onchange doc from original crowdsourcing HTML
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    st=''

    cmuoa=i.get('crowd_module_uoa','')
    ckey=i.get('crowd_key','')

    conc=i.get('crowd_on_change','')
    if conc=='':
        conc=onchange

    hi_uid=i.get('highlight_uid','')

    h='<hr>\n'
    h+='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

    h+=hextra

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    st=''

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # List entries
    ii={'action':'search',
        'module_uoa':work['self_module_uid'],
        'add_meta':'yes'}

    if cmuoa!='':
        ii['module_uoa']=cmuoa

    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    # Check unique entries
    choices={}
    mchoices={} # cache of UID -> alias choices
    wchoices={}

    for q in lst:
        d=q['meta']
        meta=d.get('meta',{})

        for kk in selector:
            kx=kk['key']
            k=ckey+kx

            if k not in choices: 
                choices[k]=[]
                wchoices[k]=[{'name':'','value':''}]

            v=meta.get(kx,'')
            if v!='':

                if v not in choices[k]: 
                    choices[k].append(v)

                    muoa=kk.get('module_uoa','')
                    vv=v
                    if muoa!='':
                        if k not in mchoices:
                            mchoices[k]={}

                        vv=mchoices[k].get(v,'')
                        if vv=='':
                            r=ck.access({'action':'load',
                                         'module_uoa':muoa,
                                         'data_uoa':v})
                            if r['return']==0:
                                mk=kk.get('module_key','')
                                if mk=='': mk='##data_name'

                                rx=ck.get_by_flat_key({'dict':r, 'key':mk})
                                if rx['return']>0: return rx
                                vv=rx['value']

                        if vv=='' or vv==None: vv=v

                        mchoices[k][v]=vv

                    wchoices[k].append({'name':vv, 'value':v})

    # Prepare query div ***************************************************************
    if cmuoa=='':
        # Start form + URL (even when viewing entry)
        r=ck.access({'action':'start_form',
                     'module_uoa':cfg['module_deps']['wfe'],
                     'url':url1,
                     'name':form_name})
        if r['return']>0: return r
        h+=r['html']

    for kk in selector:
        k=ckey+kk['key']
        n=kk['name']

        nl=kk.get('new_line','')
        if nl=='yes':
            h+='<br>\n<div id="ck_entries_space8"></div>\n'

        v=''
        if i.get(k,'')!='':
            v=i[k]
            kk['value']=v

        # Show hardware
        ii={'action':'create_selector',
            'module_uoa':cfg['module_deps']['wfe'],
            'data':wchoices.get(k,[]),
            'name':k,
            'onchange':conc, 
            'skip_sort':'no',
            'selected_value':v}
        r=ck.access(ii)
        if r['return']>0: return r

        h+='<b>'+n+':</b> '+r['html'].strip()+'\n'

    # Check hidden
    if hi_uid!='':
        h+='<input type="hidden" name="highlight_uid" value="'+hi_uid+'">\n'

    h+='<br><br>'

    # Prune list ******************************************************************
    plst=[]

    for q in lst:
        d=q['meta']
        meta=d.get('meta',{})

        # Check selector
        skip=False
        for kk in selector:
            k=kk['key']
            n=kk['name']
            v=kk.get('value','')

            if v!='' and meta.get(k,'')!=v:
                skip=True

        if not skip:
            # Process raw results
            arr=d.get('all_raw_results',[])

            for g in arr:
                nn=copy.deepcopy(q)

                ih=g.get('image_height',0)
                iw=g.get('image_width',0)

                it=0
                if ih!=0 and iw!=0:
                    it=ih*iw

                key=str(ih)+' x '+str(iw)

                prd=g.get('prediction','')
                if prd!='':
                    j1=prd.find('\n')
                    if j1>0:
                        j2=prd.find('\n',j1+1)
                        if j2>0:
                            prd=prd[j1:j2]

                # Check timing - currently temporal ugly hack
                t=g.get('time',[])

                tmin=0
                tmax=0

                if len(t)>0:
                    tmin=min(t)/1E3
                    tmax=max(t)/1E3

                nn['extra']={'key':key, 'raw_results':g, 'time_min':tmin, 'time_max':tmax, 'prediction':prd}

                plst.append(nn)

    # Check if too many
    lplst=len(plst)
    if lplst==0:
        h+='<b>No results found!</b>'
        return {'return':0, 'html':h, 'style':st}
    elif lplst>50:
        h+='<b>Too many entries to show ('+str(lplst)+') - please, prune list further!</b>'
        return {'return':0, 'html':h, 'style':st}

    # Prepare table
    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    ha='align="center" valign="top"'
    hb='align="left" valign="top"'

    h+='  <tr style="background-color:#dddddd">\n'
    h+='   <td '+ha+'><b>Data UID / Behavior UID</b></td>\n'
    h+='   <td '+ha+'><b>Crowd scenario</b></td>\n'
    h+='   <td '+ha+'><b>Model weight size</b></td>\n'
    h+='   <td '+ha+'><b>Min/Max recognition time (sec.)</b></td>\n'
    h+='   <td '+ha+'><b>Image features</b></td>\n'
    h+='   <td '+ha+'><b>Predictions</b></td>\n'
    h+='   <td '+ha+'><b>Platform</b></td>\n'
    h+='   <td '+ha+'><b>CPU</b></td>\n'
    h+='   <td '+ha+'><b>GPU</b></td>\n'
    h+='   <td '+ha+'><b>OS</b></td>\n'
    h+='   <td '+ha+'><b>Mispredictions / unexpected behavior</b></td>\n'
    h+='   <td '+ha+'><b>User</b></td>\n'
    h+='  <tr>\n'

    # Dictionary to hold target meta
    tm={}

    ix=0
    bgraph={'0':[]} # Just for graph demo
    if hi_uid!='':
        bgraph['1']=[]

    # Sort
    splst=sorted(plst, key=lambda x: x.get('extra',{}).get('time_min',0))

    cache_meta={}

    for q in splst:
        ix+=1

        duid=q['data_uid']
        path=q['path']

        d=q['meta']

        meta=d.get('meta',{})

        extra=q['extra']
        img=extra.get('img',{})
        rres=extra.get('raw_results',{})

        mp=rres.get('mispredictions',[])

        key=extra.get('key','')

        buid=rres.get('behavior_uid','')
        pred=extra.get('prediction','').replace(' ','&nbsp;')
        user=rres.get('user','')

        tmin=extra.get('time_min',0)
        tmax=extra.get('time_max',0)

        scenario=meta.get('crowd_uid','')

        plat_name=meta.get('plat_name','')
        cpu_name=meta.get('cpu_name','')
        os_name=meta.get('os_name','')
        gpu_name=meta.get('gpu_name','')
        gpgpu_name=meta.get('gpgpu_name','')

        plat_uid=meta.get('platform_uid','')
        cpu_uid=meta.get('cpu_uid','')
        os_uid=meta.get('os_uid','')
        gpu_uid=meta.get('gpu_uid','')
        gpgpu_uid=meta.get('gpgpu_uid','')

        te=d.get('characteristics',{}).get('run',{})

#        bgc='afffaf'
        bgc='dfffdf'
        bg=' style="background-color:#'+bgc+';"'

        h+='  <tr'+bg+'>\n'

        x=work['self_module_uid']
        if cmuoa!='': x=cmuoa
        h+='   <td '+ha+'>'+str(ix)+')&nbsp;<a href="'+url0+'&wcid='+x+':'+duid+'">'+duid+' / '+buid+'</a></td>\n'

        # Output scenario
        xx=mchoices.get(ckey+'crowd_uid',{}).get(scenario,'')

        kscenario=cfg['module_deps']['experiment.scenario.mobile']+':'+scenario
        if kscenario not in cache_meta:
            r=ck.access({'action':'load',
                         'module_uoa':cfg['module_deps']['experiment.scenario.mobile'],
                         'data_uoa':scenario})
            if r['return']>0: return r
            xd=r['dict']
            cache_meta[kscenario]=xd

            # Find model size
            for q in xd.get('files',[]):
                if q.get('model_weights','')=='yes':
                    xd['model_weights_size']=int(q.get('file_size',0)/1E6)
                    break

        xd=cache_meta[kscenario]

        xx=xd.get('title','')
        xy=int(xd.get('model_weights_size',0))+1

        h+='   <td '+ha+'><a href="'+url0+'&wcid='+kscenario+'">'+xx+'</a></td>\n'

        h+='   <td '+ha+'>'+str(xy)+' MB</td>\n'

        # Check relative time
        xx='<b>'+('%.3f'%tmin)+'</b>&nbsp;/&nbsp;'+('%.3f'%tmax)

        if tmin==0: xx+='<br><b><center>bug?</center></b>\n'

        if duid==hi_uid:
            if hi_uid!='':
                bgraph['0'].append([ix,None])
                bgraph['1'].append([ix,tmin])
        else:
            bgraph['0'].append([ix,tmin])
            if hi_uid!='': bgraph['1'].append([ix,None])

        h+='   <td '+ha+'>'+xx+'</a></td>\n'

        # All images
        h+='   <td '+ha+'>'+key.replace(' ','&nbsp;')+'</a></td>\n'
        h+='   <td '+ha+'>'+pred+'</a></td>\n'

        # Platform, etc ...
        x=plat_name
        if plat_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform']+':'+plat_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=cpu_name
        if cpu_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform.cpu']+':'+cpu_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=gpu_name
        if gpu_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform.gpu']+':'+gpu_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=os_name
        if os_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform']+':'+os_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=''
        for q in mp:
            ca=q.get('correct_answer','')
            mi=q.get('mispredicted_image','')
            mr=q.get('misprediction_results','')

            if mr!='':
                j1=mr.find('\n')
                if j1>0:
                    j2=mr.find('\n',j1+1)
                    if j2>0:
                        mr=mr[j1:j2]

            xx=ca
            if mi!='':
                y=work['self_module_uid']
                if cmuoa!='': y=cmuoa
                url=url0+'action=pull&common_action=yes&cid='+y+':'+duid+'&filename='+mi

                if ca=='': ca='<i>unknown</i>'
                xx='<a href="'+url+'">'+ca+'</a>'

            if x!='':
                x+='<hr>\n'

            x+='<strike>'+mr+'</strike><br>'+xx+'<br>\n'

        if tmin==0: x+='<br><b><center>Bug detected</center></b>\n'

        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='   <td '+ha+'><a href="'+url0+'&action=index&module_uoa=wfe&native_action=show&native_module_uoa=experiment.user">'+user+'</a></td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    if cmuoa=='':
        h+='</form>\n'

    if len(bgraph['0'])>0:
       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['graph'],

           "table":bgraph,

           "ymin":0,

           "ignore_point_if_none":"yes",

           "plot_type":"d3_2d_bars",

           "display_y_error_bar":"no",

           "title":"Powered by Collective Knowledge",

           "axis_x_desc":"Experiment",
           "axis_y_desc":"Unoptimized Caffe CPU classification time (s)",

           "plot_grid":"yes",

           "d3_div":"ck_interactive",

           "image_width":"900",
           "image_height":"400",

           "wfe_url":url0}

       r=ck.access(ii)
       if r['return']==0:
          x=r.get('html','')
          if x!='':
             st+=r.get('style','')

             h+='<br>\n'
             h+='<center>\n'
             h+='<div id="ck_box_with_shadow" style="width:920px;">\n'
             h+=' <div id="ck_interactive" style="text-align:center">\n'
             h+=x+'\n'
             h+=' </div>\n'
             h+='</div>\n'
             h+='</center>\n'

    return {'return':0, 'html':h, 'style':st}

##############################################################################
# process raw results from mobile devices

def process(i):
    """
    Input:  {
              TBD
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy

#    ck.save_json_to_file({'json_file':'/tmp/xyz1.json','dict':i})

    crowd_uid=i.get('crowd_uid','')
    email=i.get('email','')
    raw_results=i.get('raw_results',{})

    features=i.get('platform_features',{})

    fplat=features.get('platform',{})
    fos=features.get('os',{})
    fcpu=features.get('cpu',{})
    fgpu=features.get('gpu',{})

    plat_name=fplat.get('name','')
    plat_uid=features.get('platform_uid','')
    os_name=fos.get('name','')
    os_uid=features.get('os_uid','')
    gpu_uid=features.get('gpu_uid','')
    cpu_name=fcpu.get('name','')
    cpu_abi=fcpu.get('cpu_abi','')
    if cpu_name=='' and cpu_abi!='': 
        cpu_name='unknown-'+fcpu.get('cpu_abi','')
    cpu_uid=features.get('cpu_uid','')
    gpu_name=fgpu.get('name','')
    gpgpu_name=''
    gpgpu_uid=''
    sn=fos.get('serial_number','')

    # Prepare high-level experiment meta
    meta={'cpu_name':cpu_name,
          'os_name':os_name,
          'plat_name':plat_name,
          'gpu_name':gpu_name,
          'gpgpu_name':gpgpu_name,
          'crowd_uid':crowd_uid}

    mmeta=copy.deepcopy(meta)

    # Extra meta which is not used to search similar case ...
    mmeta['platform_uid']=plat_uid
    mmeta['os_uid']=os_uid
    mmeta['cpu_uid']=cpu_uid
    mmeta['gpu_uid']=gpu_uid
    mmeta['gpgpu_uid']=gpgpu_uid

    # Generate behavior UID
    rx=ck.gen_uid({})
    if rx['return']>0: return rx
    buid=rx['data_uid']

    raw_results['user']=email
    raw_results['behavior_uid']=buid

    # Check if already exists
    duid=''
    ddd={}

    ii={'action':'search',
        'module_uoa':work['self_module_uid'],
        'repo_uoa':rrepo,
        'search_dict':{'meta':meta},
        'add_meta':'yes'}
    rx=ck.access(ii)
    if rx['return']>0: return rx

    lst=rx['lst']

    if len(lst)==1:
        duid=lst[0]['data_uid']
        ddd=lst[0]['meta']
    else:
        rx=ck.gen_uid({})
        if rx['return']>0: return rx
        duid=rx['data_uid']

    # We keep time1,2,3 just for compatibility with the first beta version
    t=raw_results.get('time',[])
    tx=raw_results.get('time1',None)
    if tx!=None: t.append(tx)
    tx=raw_results.get('time2',None)
    if tx!=None: t.append(tx)
    tx=raw_results.get('time3',None)
    if tx!=None: t.append(tx)
    raw_results['time']=t

    # Process results
    results=ddd.get('all_raw_results',[])

    # Check if already exists with this image topology
    found=False
    for q in results:
        if q.get('image_height',None)==raw_results.get('image_height',None) and \
           q.get('image_width',None)==raw_results.get('image_width',None):
            t=q.get('time',[])

            for tx in raw_results.get('time',[]):
                t.append(tx)
            q['time']=t

            buid=q.get('behavior_uid','')

            found=True

    if not found:
        results.append(raw_results)

    ddd['all_raw_results']=results

    xmeta=ddd.get('meta',{})
    xmeta.update(mmeta)
    ddd['meta']=xmeta

    # Update meta
    rx=ck.access({'action':'update',
                  'module_uoa':work['self_module_uid'],
                  'data_uoa':duid,
                  'repo_uoa':rrepo,
                  'dict':ddd,
                  'substitute':'yes',
                  'sort_keys':'yes'})
    if rx['return']>0: return rx

    return {'return':0, 'status':'Results successfully added to Collective Knowledge (UID='+duid+')!', 'data_uid':duid, 'behavior_uid':buid}

##############################################################################
# record unexpected behavior

def process_unexpected_behavior(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    duid=i.get('data_uid','')
    buid=i.get('behavior_uid','')
    cuid=i.get('crowd_uid','')
    rres=i.get('raw_results','')
    ca=i.get('correct_answer','')
    file_base64=i.get('file_base64','')

    # Find data
    r=ck.access({'action':'load',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duid})
    if r['return']>0: return r
    d=r['dict']
    p=r['path']

    # Find behavior
    found=False
    arr=d.get('all_raw_results',[])
    for q in arr:
        if q.get('behavior_uid','')==buid:
            found=True
            break

    if not found:
        return {'return':1, 'error':'can\'t find behavior '+buid+' in entry '+duid}

    # Generate UID for the file with unexpected behavior
    rx=ck.gen_uid({})
    if rx['return']>0: return rx

    ff='misprediction-image-'+rx['data_uid']+'.jpg'

    pf=os.path.join(p,ff)

    mp=q.get('mispredictions',[])

    qq={}
    qq['misprediction_results']=rres
    qq['mispredicted_image']=ff
    qq['correct_answer']=ca

    mp.append(qq)

    q['mispredictions']=mp

    # Record file
    rx=ck.convert_upload_string_to_file({'file_content_base64':file_base64,
                                         'filename':pf})
    if rx['return']>0: return rx

    # Update entry (should add lock in the future for parallel processing)
    r=ck.access({'action':'update',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duid,
                 'dict':d,
                 'sort_keys':'yes',
                 'substitute':'yes',
                 'ignore_update':'yes'})
    if r['return']>0: return r

    return {'return':0}

##############################################################################
# generate scenario to crowdsource benchmarking/optimization of Caffe on Android devices

def generate(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy
    import shutil

    o=i.get('out','')

    # Get platform params
    ck.out('Detecting host platform info ...')
    ck.out('')

    i['action']='detect'
    i['module_uoa']=cfg['module_deps']['platform']
    i['out']=''
    rpp=ck.access(i)
    if rpp['return']>0: return rpp

    hos=rpp['host_os_uoa']
    hosd=rpp['host_os_dict']

    # Search all scenarios
    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['experiment.scenario.mobile'],
                 'add_meta':'yes'})
    if r['return']>0: return r

    lst=r['lst']
    if len(lst)==0:
       return {'return':1, 'error':'no pre-recorded Caffe crowd-scenarios found ...'}

    uids={}
    found=False

    engine_meta={}

    # Go through required ABIs and compile classification and libcaffe.so
    for b in abis:
        abi=b['abi']
        os_uoa=b['os_uoa']

        ck.out(line)
        ck.out('Preparing Caffe with ABI "'+abi+'" for crowd-benchmarking and crowd-tuning ...')

        # Compile classification (should compile all deps)
        ck.out('')
        ck.out('Compiling classification and Caffe ...')

        ii={'action':'compile',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':cfg['data_deps']['caffe-classification-android'],
            'host_os':hos,
            'target_os':os_uoa,
            'speed':'yes',
            'out':o}
        r=ck.access(ii)
        if r['return']>0: return r

        # Get various info
        cc=r.get('characteristics',{})

        cs=cc.get('compilation_success','')
        if cs!='yes':
           return {'return':1, 'error':'compilation failed'}

        md5=cc.get('md5_sum','')
        bs=cc.get('binary_size',0)

        misc=r.get('misc',{})

        pf=misc.get('path','')
        td=misc.get('tmp_dir','')
        of=misc.get('target_exe','')
        pv=misc.get('program_version','')

        pp=os.path.join(pf,td,of)
        if not os.path.isfile(pp):
           return {'return':1, 'error':'target binary not found ('+pp+')'}

        # Get info about deps
        deps=r.get('deps',{})

        # libcaffe
        cdeps=deps.get('lib-caffe',{})

        cfp=cdeps.get('cus',{}).get('full_path','')

        # Force .so (sometimes points to .a)
        cfp=os.path.join(os.path.dirname(cfp),libcaffe)

        if not os.path.isfile(cfp):
           return {'return':1, 'error':'Caffe lib not found ('+cfp+')'}

        r=ck.run_and_get_stdout({'cmd':hosd['md5sum']+' '+cfp, 
                                 'shell':'no'})
        if r['return']>0: return r
        sto=r['stdout'].split(' ')

        if len(sto)==0:
           return {'return':1, 'error':'can\'t get MD5 of libcaffe.so'}

        lmd5=sto[0] # MD5 of caffe lib

        ls=os.path.getsize(cfp)

        # xopenme
        odeps=deps.get('xopenme',{})

        ofp=odeps.get('cus',{}).get('full_path','')

        # Force .so (sometimes points to .a)
        ofp=os.path.join(os.path.dirname(ofp),libxopenme)

        if not os.path.isfile(ofp):
           return {'return':1, 'error':'xopenme plugin not found ('+ofp+')'}

        r=ck.run_and_get_stdout({'cmd':hosd['md5sum']+' '+ofp, 
                                 'shell':'no'})
        if r['return']>0: return r
        sto=r['stdout'].split(' ')

        if len(sto)==0:
           return {'return':1, 'error':'can\'t get MD5 of librtlxopenme.so'}

        omd5=sto[0] # MD5 of caffe lib

        ops=os.path.getsize(ofp)

        # Get versions of all deps
        dv={}
        for x in deps:
            dv[x]={}
            cx=deps[x].get('cus',{})

            dv[x]['version']=cx.get('version','')
            dv[x]['revision']=cx.get('git_info',{}).get('revision','')
            dv[x]['iso_datetime_cut_revision']=cx.get('git_info',{}).get('iso_datetime_cut_revision','')
            dv[x]['tags']=deps[x].get('tags',[])

        # Prepare info pack about this experiment
        meta={'classification_version':pv,
              'deps':dv,
              'host_os':hos,
              'target_os':os_uoa}

        # Search caffe original code with a given ABI
        ck.out('')
        ck.out('Checking / updating scenario files ...')

        changed_files=[] # Which libs were substituted

        for q in lst:
           duid=q['data_uid']
           duoa=q['data_uoa']
           ruoa=q['repo_uid']

           d=q['meta']

           if d.get('outdated','')=='yes': # skip archived entries
              continue

           pe=q['path'] # Path to entry

           files=d.get('files',[])

           for ff in files:
               fduoa=ff.get('from_data_uoa','')
               if fduoa=='':
                  sabi=ff.get('supported_abi',[])
                  if abi in sabi:
                     fn=ff.get('filename','')
                     p=ff.get('path','')

                     xfs=ff.get('file_size',0)
                     xmd5=ff.get('md5','')

                     if (fn==libcaffe and (xmd5!=lmd5 and xfs!=ls)) or \
                        (fn=='classification' and (xmd5!=md5 and xfs!=bs)) or \
                        (fn==libxopenme and (xmd5!=omd5 and xfs!=ops)):

                        if not found:
                           # If first time, tell that old scenario will be removed!
                           ck.out('')
                           ck.out('WARNING: we found old files and will be removing them.')
                           ck.out('         Make sure that you archived them!')

                           ck.out('')
                           r=ck.inp({'text':'Would you like to proceed and remove old files (y/N): '})
                           if r['return']>0: return r

                           s=r['string'].strip().lower()

                           if s!='y' and s!='yes':
                              return {'return':0}

                           found=True

                        ck.out('')
                        ck.out('Updating '+fn+' in '+duoa+' ('+p+')')

                        oduid=p.split('/')[1]

                        nduid=uids.get(oduid,'')

                        # Generate new UID
                        if nduid=='':
                           r=ck.gen_uid({})
                           if r['return']>0: return r
                           nduid=r['data_uid']

                           uids[oduid]=nduid

                           ck.out('  * New code UID for '+oduid+' : '+nduid)

                        np=os.path.join(pe,'code',nduid,abi)
                        ck.out('  * New path: '+np)

                        # Create new dir and copy file
                        if not os.path.isdir(np):
                           os.makedirs(np)

                        fnp=os.path.join(np,fn)

                        if fn==libcaffe:
                           shutil.copy(cfp, fnp)
                        elif fn=='classification':
                           shutil.copy(pp, fnp)
                        else:
                           shutil.copy(ofp, fnp)

                        # Remove old path
                        px=os.path.join(pe,p)
                        if os.path.isdir(px):
                           ck.out('  * Removing dir: '+px)
                           shutil.rmtree(px)

                        # If whole directory is empty, remove it too
                        px=os.path.join(pe,'code',oduid)
                        if os.path.isdir(px) and len(os.listdir(px))==0:
                           ck.out('  * Removing dir: '+px)
                           shutil.rmtree(px)

                        # Changing meta
                        zp=np
                        if not zp.startswith('code') and not zp.startswith('data'):
                           j1=zp.find('code/')
                           if j1<0:
                              j1=zp.find('data/')
                           if j1>0:
                              zp=zp[j1:]

                        changed_before={'filename':fn,
                                        'from_data_uoa':duid,
                                        'path':p,
                                        'file_size':xfs,
                                        'md5':xmd5}

                        changed_after={'filename':fn,
                                       'from_data_uoa':duid,
                                       'path':zp}

                        if fn==libcaffe:
                           changed_after['file_size']=ls
                           changed_after['md5']=lmd5
                        elif fn=='classification':
                           changed_after['file_size']=bs
                           changed_after['md5']=md5
                        else:
                           changed_after['file_size']=ops
                           changed_after['md5']=omd5

                        ff.update(changed_after)
                        del(ff['from_data_uoa'])

                        # Updating global meta of engine
                        engine_meta[abi]={'program_version':pv, 'deps_versions':dv}

                        d['engine_meta']=engine_meta

                        # Add to changed
                        changed_files.append({'before':changed_before,
                                              'after':changed_after})

        # If changed original files, change them in all other meta
        if len(changed_files)>0:

           for q in lst:
               duid=q['data_uid']
               duoa=q['data_uoa']
               muid=q['module_uid']
               ruoa=q['repo_uid']

               d=q['meta']

               if d.get('outdated','')=='yes': # skip archived entries
                  continue

               d['engine_meta']=engine_meta

               pp=q['path'] # Path to entry

               files=d.get('files',[])

               for ff in files:
                   fduoa=ff.get('from_data_uoa','')

                   if fduoa!='':
                      # Check if needs to be changed ...
                      for c in changed_files:
                          before=c['before']
                          after=c['after']

                          rx=ck.compare_dicts({'dict1':ff, 'dict2':before})
                          if rx['return']>0: return rx
                          if rx['equal']=='yes':
                             ff.update(after)

               # Update entry now (aggregating all above changes)
               r=ck.access({'action':'update',
                            'module_uoa':muid,
                            'data_uoa':duid,
                            'repo_uoa':ruoa,
                            'dict':d,
                            'substitute':'yes',
                            'ignore_update':'yes',
                            'sort_keys':'yes'})
               if r['return']>0: return r

    return {'return':0}
