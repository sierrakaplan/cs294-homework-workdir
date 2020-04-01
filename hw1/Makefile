geniedir ?= ..
thingpedia ?= thingpedia

memsize := $(shell echo $$(($$(grep MemTotal /proc/meminfo | sed 's/[^0-9]//g')/1000-2500)))
genie = node --experimental_worker --max_old_space_size=$(memsize) $(geniedir)/tool/genie.js

experiment ?= restaurants

template_file ?= thingtalk/en/thingtalk.genie
dataset_file ?= emptydataset.tt

synthetic_flags ?= projection_with_filter projection aggregation schema_org filter_join multifilter multifilters no_stream

class_name = Restaurant
white_list = restaurant,review

generate_flags = $(foreach v,$(synthetic_flags),--set-flag $(v)) --white-list $(white_list)

$(experiment)/schema.org.tt: $(geniedir)/tool/webqa-process-schemaorg.js
	$(genie) webqa-process-schemaorg -o $@ --class-name $(class_name)

emptydataset.tt:
	echo 'dataset @empty {}' > $@

$(experiment)/data.json : $(experiment)/schema.org.tt source-data/$(experiment)/*.json $(geniedir)/tool/webqa-normalize-data.js
	$(genie) webqa-normalize-data -o $@ --thingpedia $(experiment)/schema.org.tt source-data/$(experiment)/*.json
	
$(experiment)/schema.tt : $(experiment)/schema.org.tt $(experiment)/data.json
	$(genie) webqa-trim-class --thingpedia $(experiment)/schema.org.tt -o $@ --data ./$(experiment)/data.json --entities $(experiment)/entities.json

$(experiment)/constants.tsv: $(experiment)/parameter-datasets.tsv $(experiment)/schema.tt
	$(genie) sample-constants -o $@ --parameter-datasets $(experiment)/parameter-datasets.tsv --thingpedia $(experiment)/schema.tt --devices org.schema.$(class_name)
	cat $(geniedir)/data/en-US/constants.tsv >> $@

$(experiment)/synthetic-for-turking.tsv : $(experiment)/schema.tt emptydataset.tt $(geniedir)/languages/thingtalk/en/*.genie
	$(genie) generate \
	  --template $(geniedir)/languages/$(template_file) \
	  --thingpedia $(experiment)/schema.tt --entities $(experiment)/entities.json --dataset emptydataset.tt \
	  --target-pruning-size 200 \
	  -o $@.tmp $(generate_flags) --set-flag turking  --maxdepth 7
	mv $@.tmp $@
	
$(experiment)/synthetic-for-turking-sampled.tsv : $(experiment)/synthetic-for-turking.tsv $(experiment)/constants.tsv $(experiment)/schema.tt
	$(genie) sample --thingpedia $(experiment)/schema.tt -o $@.tmp --constants $(experiment)/constants.tsv --sampling-strategy bySentence $<
	mv $@.tmp $@

mturk-paraphrasing.csv: $(experiment)/synthetic-for-turking-sampled.tsv
	bash -c 'cat <(head -n1 $< ) <(tail -n+2 $< | shuf | head -n 500)' | $(genie) mturk-make-paraphrase-hits -o $@

$(experiment)/synthetic-d%.tsv: $(experiment)/schema.tt $(dataset_file) $(geniedir)/languages/thingtalk/en/*.genie
	$(genie) generate \
	  --template $(geniedir)/languages/$(template_file) \
	  --thingpedia $(experiment)/schema.tt --entities $(experiment)/entities.json --dataset $(dataset_file) \
	  --target-pruning-size 200 \
	  -o $@.tmp $(generate_flags) --maxdepth $$(echo $* | cut -f1 -d'-') --random-seed $@
	mv $@.tmp $@

$(experiment)/synthetic.tsv : $(foreach v,1 2 3,$(experiment)/synthetic-d6-$(v).tsv) $(experiment)/synthetic-d8.tsv
	cat $^ > $@


shared-parameter-datasets.tsv:
	$(thingpedia) --url https://almond.stanford.edu/thingpedia --developer-key $(developer_key) --access-token invalid \
	  download-entity-values --manifest $@ --append-manifest -d shared-parameter-datasets
	$(thingpedia) --url https://almond.stanford.edu/thingpedia --developer-key $(developer_key) --access-token invalid \
	  download-string-values --manifest $@ --append-manifest -d shared-parameter-datasets

$(experiment)/parameter-datasets.tsv : $(experiment)/schema.tt $(experiment)/data.json shared-parameter-datasets.tsv
	$(genie) webqa-make-string-datasets --manifest $@ -d $(experiment)/parameter-datasets --thingpedia $(experiment)/schema.tt --data $(experiment)/data.json --class-name $(class_name)
	sed 's|\tshared-parameter-datasets|\t../shared-parameter-datasets|g' shared-parameter-datasets.tsv >> $@

clean:
	rm -rf $(experiment)/synthetic* $(experiment)/data.json $(experiment)/entities.json $(experiment)/parameter-datasets* $(experiment)/schema.org.tt $(experiment)/schema.tt $(experiment)/everything.tsv $(experiment)/constants.tsv

