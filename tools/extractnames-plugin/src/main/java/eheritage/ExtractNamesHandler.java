package eheritage;

import static org.elasticsearch.rest.RestRequest.Method.POST;
import static org.elasticsearch.rest.RestStatus.CREATED;
import static org.elasticsearch.rest.RestStatus.OK;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang3.StringUtils;
import org.elasticsearch.action.ActionListener;
import org.elasticsearch.action.get.GetRequest;
import org.elasticsearch.action.get.GetResponse;
import org.elasticsearch.action.update.UpdateRequest;
import org.elasticsearch.action.update.UpdateResponse;
import org.elasticsearch.client.Client;
import org.elasticsearch.common.inject.Inject;
import org.elasticsearch.common.xcontent.XContentBuilder;
import org.elasticsearch.common.xcontent.XContentBuilderString;
import org.elasticsearch.common.xcontent.json.JsonXContent;
import org.elasticsearch.rest.RestChannel;
import org.elasticsearch.rest.RestController;
import org.elasticsearch.rest.RestHandler;
import org.elasticsearch.rest.RestRequest;
import org.elasticsearch.rest.RestStatus;
import org.elasticsearch.rest.XContentRestResponse;
import org.elasticsearch.rest.XContentThrowableRestResponse;
import org.elasticsearch.rest.action.support.RestXContentBuilder;

import com.google.common.collect.Lists;

public class ExtractNamesHandler implements RestHandler {

  private static final String EXTRACTED_NAMES = "extracted_names";

  private final Client client;

  private static final class Fields {
    static final XContentBuilderString _INDEX = new XContentBuilderString("_index");
    static final XContentBuilderString _TYPE = new XContentBuilderString("_type");
    static final XContentBuilderString _ID = new XContentBuilderString("_id");
    static final XContentBuilderString _VERSION = new XContentBuilderString("_version");
    static final XContentBuilderString _MSG = new XContentBuilderString("_msg");
    static final XContentBuilderString _EXTRACTED = new XContentBuilderString("_extracted");
    
  }

  @Inject
  public ExtractNamesHandler(RestController controller, Client client) {
    controller.registerHandler(POST, "/{index}/{type}/{id}/_extractnames", this);
    this.client = client;
  }

  @Override
  public void handleRequest(final RestRequest request, final RestChannel channel) {
    try {
      GetResponse document = client.get(new GetRequest(request.param("index"),
          request.param("type"), request.param("id"))).get();
      if(document != null && (!document.isSourceEmpty())) {
        final List<String> names =extractNames(filter(document.getSourceAsMap()));
        if(updateRequired(names(names), extractedNames(document.getSourceAsMap()))) {
          UpdateRequest updateRequest = new UpdateRequest(request.param("index"),
              request.param("type"), request.param("id"));
          updateRequest.source(content(names));
          client.update(updateRequest, new ActionListener<UpdateResponse>() {
            @Override
            public void onResponse(UpdateResponse response) {
              try {
                XContentBuilder builder = RestXContentBuilder.restContentBuilder(request);
                builder.startObject()
                        .field(Fields._INDEX, response.getIndex())
                        .field(Fields._TYPE, response.getType())
                        .field(Fields._ID, response.getId())
                        .field(Fields._VERSION, response.getVersion())
                        .field(Fields._EXTRACTED, names(names));
                builder.endObject();
                RestStatus status = OK;
                if (response.isCreated()) {
                    status = CREATED;
                }
                channel.sendResponse(new XContentRestResponse(request, status, builder));
              } catch(Throwable t) {
                onFailure(t);
              }
            }

            @Override
            public void onFailure(Throwable e) {
              try {
                channel.sendResponse(new XContentThrowableRestResponse(request, e));
              } catch (IOException e1) {
                e1.printStackTrace();
              }
            }
          });
        } else {
          channel.sendResponse(new XContentRestResponse(request, RestStatus.OK,
              noUpdateResponse(request, names(names))));
        }
      } else {
        channel.sendResponse(new XContentRestResponse(request, RestStatus.NOT_FOUND, 
            JsonXContent.contentBuilder().startObject().field(Fields._MSG, "not found").endObject()));
      }
    } catch(Exception e) {
      e.printStackTrace();
    }
  }

  private XContentBuilder noUpdateResponse(RestRequest request, String names) throws IOException {
    XContentBuilder builder = JsonXContent.contentBuilder();
    builder.startObject()
    .field(Fields._INDEX, request.param("index"))
    .field(Fields._TYPE, request.param("type"))
    .field(Fields._ID, request.param("id"))
    .field(Fields._EXTRACTED, names)
    .field(Fields._MSG, "no update required");
    builder.endObject();
    return builder;
  }

  private String extractedNames(Map<String, Object> fields) {
    Object o = fields.get(EXTRACTED_NAMES);
    return (o instanceof String)?(String)o:null;
  }

  private boolean updateRequired(String names, String stored) {
    String s1 = names != null? names: "";
    String s2 = stored != null? stored: "";
    return !StringUtils.equals(s1, s2);
  }

  private XContentBuilder content(List<String> names) throws IOException {
    XContentBuilder builder = JsonXContent.contentBuilder();
    builder.startObject();
    builder.startObject("doc");
    builder.field("extracted_names", names(names));
    builder.endObject();
    builder.endObject();
    return builder;
  }

  private String names(List<String> names) {
    return StringUtils.join(names, ',');
  }

  private Map<String, Object> filter(Map<String, Object> fields) {
    return fields;
  }

  private List<String> extractNames(Map<String, Object> fields) {
    NameExtractor extractor = new NameExtractor();
    List<String> names = Lists.newArrayList();
    for(Map.Entry<String, Object> me : fields.entrySet()) {
      String key = me.getKey();
      if(!StringUtils.equalsIgnoreCase(EXTRACTED_NAMES, key)) {
        Object o = me.getValue();
        if(o instanceof String) {
          names.addAll(extractor.getNames((String)o));
        }
      }
    }
    return names;
  }
}
