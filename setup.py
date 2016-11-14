import fileinput, re, json, argparse, os


def load_envs_from_machine():
  print "# Using env from machine"
  return os.environ


def load_envs_from_file(envfile):
  print "# Loading env from " + envfile
  ret = {}
  for line in fileinput.input(envfile):
    line = line.strip()
    eq = line.index("=")
    key = line[0:eq]
    val = line[eq+1:]
    ret[key] = val
  return ret


def parse_env(envs):
  re_virtual_host = re.compile("^([A-Z0-9_]+)_([0-9]+)_ENV_VIRTUAL_HOST")
  re_virtual_addr = re.compile("^([A-Z0-9_]+)_([0-9]+)_PORT_([0-9]+)_TCP_ADDR")
  re_virtual_port = re.compile("^([A-Z0-9_]+)_([0-9]+)_PORT_([0-9]+)_TCP_PORT")
  re_server_crt = re.compile("^([A-Z0-9_\.]+)_SERVER_CRT")
  re_server_key = re.compile("^([A-Z0-9_\.]+)_SERVER_KEY")
  re_server_dom = re.compile("^([A-Z0-9_\.]+)_SERVER_DOMAIN")
  re_target = re.compile("^target\.([0-9]+)\.([a-z]+)")
  vhosts = {}
  vhostkvp = {}
  domaincerts = {}

  for key in envs:
    val = envs[key]

    r = re_virtual_host.match(key)
    if r:
      vhostkey = r.group(1)
      vhostprop = "domains"
      # print "virtual host:", r.group(1), r.group(2), val
      if not vhosts.has_key(vhostkey):
        vhosts[vhostkey] = {}
      vhosts[vhostkey][vhostprop] = val.split(",")
      continue

    r = re_virtual_addr.match(key)
    if r:
      vhostkey = r.group(1)
      vhostprop = "target." + r.group(2)+".addr"
      # print "virtual addr:", r.group(1), r.group(2), r.group(3), val
      if not vhosts.has_key(vhostkey):
        vhosts[vhostkey] = {}
      if not vhosts[vhostkey].has_key("targets"):
        vhosts[vhostkey]["targets"] = {}
      if not vhosts[vhostkey]["targets"].has_key(r.group(2)):
        vhosts[vhostkey]["targets"][r.group(2)] = {}
      vhosts[vhostkey]["targets"][r.group(2)]["addr"] = val
      continue

    r = re_virtual_port.match(key)
    if r:
      vhostkey = r.group(1)
      vhostprop = "target." + r.group(2)+".port"
      print "virtual port:", r.group(1), r.group(2), r.group(3), val
      val = int(val)
      if not vhosts.has_key(vhostkey):
        vhosts[vhostkey] = {}
      if not vhosts[vhostkey].has_key("targets"):
        vhosts[vhostkey]["targets"] = {}
      if not vhosts[vhostkey]["targets"].has_key(r.group(2)):
        vhosts[vhostkey]["targets"][r.group(2)] = {}
      print vhosts[vhostkey]["targets"][r.group(2)]
      if "port" in vhosts[vhostkey]["targets"][r.group(2)]:
        # pick lowest port.
        if val < vhosts[vhostkey]["targets"][r.group(2)]["port"]:
          vhosts[vhostkey]["targets"][r.group(2)]["port"] = val
      else:
        vhosts[vhostkey]["targets"][r.group(2)]["port"] = val
      continue

    r = re_server_crt.match(key)
    if r:
      domainkey = r.group(1)
      # print "server ssl cert:", r.group(1), val
      if not domaincerts.has_key(domainkey):
        domaincerts[domainkey] = {}
      domaincerts[domainkey]["crt"] = val
      continue

    r = re_server_key.match(key)
    if r:
      domainkey = r.group(1)
      # print "server ssl key:", r.group(1), val
      if not domaincerts.has_key(domainkey):
        domaincerts[domainkey] = {}
      domaincerts[domainkey]["key"] = val
      continue

    r = re_server_dom.match(key)
    if r:
      domainkey = r.group(1)
      # print "server ssl dom:", r.group(1), val
      if not domaincerts.has_key(domainkey):
        domaincerts[domainkey] = {}
      domaincerts[domainkey]["domains"] = val.split(",")
      continue

  domains = []
  domainmap = {}
  for k in domaincerts:
    v = domaincerts[k]
    for testdomain in v['domains']:
      domains.append(testdomain)
      domainmap[testdomain] = k

  print "# ALL DOMAINS ", domains
  print "# ALL DOMAINMAP ", domainmap

  return {
    "vhosts": vhosts,
    "domains": domaincerts,
    "alldomains": domains,
    "domainmap": domainmap
  }


def write_certificates(data, args):
  print "# Writing certificates..."
  vhosts = data['vhosts']
  domaincerts = data['domains']
  for k in domaincerts:
    v = domaincerts[k]
    # print "# DOMAIN", k, v
    # write certs to disk

    path = "%sserver-%s.crt" % (args.certs, k)
    print "# Writing %s " % (path)
    f = open(path, "w")
    f.write(re.sub(r"\\n", '\n', v["crt"]) + '\n')
    f.close()

    path = "%sserver-%s.key" % (args.certs, k)
    print "# Writing %s " % (path)
    f = open(path, "w")
    f.write(re.sub(r"\\n", '\n', v["key"]) + '\n')
    f.close()


def get_certificate_paths(data, args, domain):
  # try to match exact
  for testdomain in data['alldomains']:
    print "# CHECKING MATCH", domain, testdomain
    if testdomain == domain:
      key = data['domainmap'][testdomain]
      return {
        "crtpath": "%sserver-%s.crt" % (args.certs, key),
        "keypath": "%sserver-%s.key" % (args.certs, key)
      }

  # if no match yet, try less strict wildcard matching
  for testdomain in data['alldomains']:
    print "# CHECKING DOMAIN ENDSWITH ", domain, testdomain
    if domain.endswith(testdomain):
      key = data['domainmap'][testdomain]
      return {
        "crtpath": "%sserver-%s.crt" % (args.certs, key),
        "keypath": "%sserver-%s.key" % (args.certs, key)
      }

  return None


def generate_config_file(data, args):
  print "# Generating config file..."
  vhosts = data['vhosts']
  domains = data['domains']
  output = ""

  for key in vhosts:
    v = vhosts[key]
    print "# VHOST", key, v
    output += "#\n# VHOST %s\n#\n\n" % (json.dumps(v))
    if 'targets' in v:
      output += "upstream %s-origin {\n" % (key)
      targets = v["targets"]
      for k2 in targets:
        output += "  server %s:%s;\n" % (targets[k2]["addr"], targets[k2]["port"])
      output += "}\n\n"

      domains = v['domains']
      for domain in domains:
        sslinfo = get_certificate_paths(data, args, domain)
        # print "# DOMAIN", domain, sslinfo
        output += "#\n# DOMAIN %s %s\n#\n\n" % (json.dumps(domain), json.dumps(sslinfo))
        output += "server {\n"
        output += "  listen 80;\n"
        output += "  server_name %s;\n" % (domain)
        output += "  location / {\n"
        output += "    proxy_pass http://%s-origin;\n" % (key)
        output += "    proxy_set_header Host $host;\n"
        output += "    proxy_set_header X-Forwarded-For $remote_addr;\n"
        output += "    proxy_next_upstream_timeout 5s;\n"
        output += "    proxy_read_timeout 10s;\n"
        output += "    proxy_send_timeout 10s;\n"
        output += "  }\n"
        output += "}\n\n"
        if sslinfo:
          output += "server {\n"
          output += "  listen 443;\n"
          output += "  server_name %s;\n" % (domain)
          output += "  ssl on;\n"
          output += "  ssl_certificate %s;\n" % (sslinfo['crtpath'])
          output += "  ssl_certificate_key %s;\n" % (sslinfo['keypath'])
          output += "  location / {\n"
          output += "    proxy_pass http://%s-origin;\n" % (key)
          output += "    proxy_set_header Host $host;\n"
          output += "    proxy_set_header X-Forwarded-For $remote_addr;\n"
          output += "    proxy_next_upstream_timeout 5s;\n"
          output += "    proxy_read_timeout 10s;\n"
          output += "    proxy_send_timeout 10s;\n"
          output += "  }\n"
          output += "}\n\n"
      else:
        print "# invalid upstream, no targets found."

  return output


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Write nginx config files.')
  parser.add_argument('--env', metavar='filename', type=str, help='read environment variables from file')
  parser.add_argument('--certs', metavar='path', type=str, help='write ssl certificates to this folder')
  parser.add_argument('--conf', metavar='filename', type=str, help='output config file')
  args = parser.parse_args()
  if not args.certs or not args.conf:
    parser.print_help()
    exit(1)

  env = load_envs_from_file(args.env) if args.env else load_envs_from_machine()
  data = parse_env(env)
  write_certificates(data, args)

  configfile = generate_config_file(data, args)
  f = open(args.conf, "w")
  f.write(configfile)
  f.close()
  exit(0)
